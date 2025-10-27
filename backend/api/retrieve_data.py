from sqlalchemy import create_engine, text
import sys
from typing import Optional

# Usage: python series.py <contour_id>
engine = create_engine("postgresql://postgres:11111@localhost:5433/postgres")


def fetch_hourly_imports(contour_id: int, day: Optional[int] = None, schema: Optional[str] = ""):
    """Return rows (contour_id, clock, energy_import) for the given contour_id
    where the timestamp is at whole hours (minute = 0). Results are ordered by clock ascending.
    """
    if day is None:
        table = f"{schema}.contour_data" if schema else "contour_data"
        sql = text(
            f"SELECT contour_id, clock, energy_import FROM {table} "
            "WHERE contour_id = :cid AND date_part('minute', clock) = 0"
            " AND date_part('day', clock) != 8 "
            "ORDER BY clock ASC"
        )
        with engine.connect() as conn:
            result = conn.execute(sql, {"cid": contour_id}).fetchall()
        return result
    else:
        table = f"{schema}.contour_data" if schema else "contour_data"
        sql = text(
            f"SELECT contour_id, clock, energy_import FROM {table} "
            "WHERE contour_id = :cid AND date_part('minute', clock) = 0"
            "  AND date_part('day', clock) = :day "
            "ORDER BY clock ASC"
        )
        with engine.connect() as conn:
            result = conn.execute(sql, {"cid": contour_id, "day": day}).fetchall()
        return result

def diff(series: list[float]) -> list[float]:
    """Return the first difference of the input series."""
    diffs: list[float] = []
    for i, j in zip(series[:-1], series[1:]):
        try:
            di = float(i)
            dj = float(j)
        except Exception:
            # skip pairs with non-numeric values
            continue
        d = dj - di
        # clamp negative values to zero because this represents energy usage
        if d < 0 or d > 1000:
            d = 10.0
        diffs.append(d)
    return diffs

def get_series(cid: int, day: Optional[int] = None) -> list[float]:
    rows = fetch_hourly_imports(cid, day)
    series = []
    for r in rows:
        series.append(r[2])

    diffs = diff(series)
    return diffs

def general_info(schema: Optional[str] = ""):
    table = f"{schema}.contour_data" if schema else "contour_data"
    sql = text(
        f"SELECT energy_import FROM {table}"
    )
    with engine.connect() as conn:
        result = conn.execute(sql).fetchall()
    series = []
    for r in result:
        series.append(r[0])

    current_usage = sum(diff(series))

    table = f"{schema}.contour_data" if schema else "contour_data"
    # COUNT(DISTINCT contour_id) returns the number of unique contour_id values
    sql = text(f"SELECT COUNT(DISTINCT contour_id) FROM {table}")
    with engine.connect() as conn:
        # scalar() returns the single aggregated value directly
        number_of_contours = conn.execute(sql).scalar()
    # ensure we return a plain int (or 0 if None)

    return current_usage, int(number_of_contours)

def regional_consumption():
    table = f"interpolated.contour c JOIN interpolated.locations l ON c.location_id = l.location_id JOIN interpolated.contour_data cd ON c.contour_id = cd.contour_id"
    sql = text(
        f"SELECT l.name, cd.energy_import FROM {table} ORDER BY l.name, cd.clock ASC"
    )
    with engine.connect() as conn:
        result = conn.execute(sql).fetchall()
    
    # Group data by location
    location_data = {}
    current_location = None
    current_series = []
    
    for name, energy_import in result:
        if name != current_location:
            # Process previous location's data if it exists
            if current_location and current_series:
                location_data[current_location] = sum(diff(current_series))
            # Start new location
            current_location = name
            current_series = []
        current_series.append(energy_import)
    
    # Process the last location
    if current_location and current_series:
        location_data[current_location] = sum(diff(current_series))

    return location_data


def calc_timeseries_from_db(schema: Optional[str] = "interpolated"):
    """Return a structure like calc.json built from the database.

    Output format:
    [
      { "LocationName": { "YYYY-MM-DD HH:MM:SS": { "Import": <value> }, ... }, ... },
      { "moldova": { "YYYY-MM-DD HH:MM:SS": <sum_of_imports_across_locations>, ... } }
    ]

    The query uses the same joins as `regional_consumption` to obtain location name,
    clock and energy_import for every record.
    """
    table = (
        f"{schema}.contour c JOIN {schema}.locations l ON c.location_id = l.location_id "
        f"JOIN {schema}.contour_data cd ON c.contour_id = cd.contour_id"
    )
    # include energy_export column as well
    sql = text(f"SELECT l.name, cd.clock, cd.energy_import, cd.energy_export FROM {table} WHERE date_part('day', clock) = 7 ORDER BY l.name, cd.clock ASC")

    with engine.connect() as conn:
        rows = conn.execute(sql).fetchall()

    per_location: dict = {}
    moldova_agg: dict = {}

    for name, clock, energy_import, energy_export in rows:
        # normalize values
        ts = str(clock)
        try:
            imp = float(energy_import) if energy_import is not None else None
        except Exception:
            imp = None
        try:
            exp = float(energy_export) if energy_export is not None else None
        except Exception:
            exp = None

        if name not in per_location:
            per_location[name] = {}

        # store import and export values under timestamp
        per_location[name][ts] = {"Import": imp, "Export": exp}

        # accumulate for moldova aggregated series
        # initialize if missing
        if ts not in moldova_agg:
            moldova_agg[ts] = {"Import": 0.0, "Export": 0.0}

        if imp is not None:
            moldova_agg[ts]["Import"] = moldova_agg[ts].get("Import", 0.0) + imp
        # if imp is None, leave sum as-is (treat missing as 0)

        if exp is not None:
            moldova_agg[ts]["Export"] = moldova_agg[ts].get("Export", 0.0) + exp
        # if exp is None, leave sum as-is

    # wrap moldova under a dict as in calc.json
    return [per_location, {"moldova": moldova_agg}]

def get_series_country(country: str, schema: Optional[str] = "interpolated") -> list[float]:
    """Return a structure like calc.json built from the database.

    Output format:
    [
      { "LocationName": { "YYYY-MM-DD HH:MM:SS": { "Import": <value> }, ... }, ... },
      { "moldova": { "YYYY-MM-DD HH:MM:SS": <sum_of_imports_across_locations>, ... } }
    ]

    The query uses the same joins as `regional_consumption` to obtain location name,
    clock and energy_import for every record.
    """
    table = (
        f"{schema}.contour c JOIN {schema}.locations l ON c.location_id = l.location_id "
        f"JOIN {schema}.contour_data cd ON c.contour_id = cd.contour_id"
    )
    # include energy_export column as well
    sql = text(f"SELECT cd.energy_import FROM {table} WHERE date_part('minute', clock) = 0 AND l.name = :country ORDER BY cd.clock ASC")

    with engine.connect() as conn:
        rows = conn.execute(sql, {"country": country}).fetchall()

    values = []
    for (energy_import,) in rows:
        try:
            imp = float(energy_import) if energy_import is not None else 0.0
        except Exception:
            imp = 0.0
        values.append(imp)

    return values

def get_location_color(location_data: dict):
            # Work on a shallow copy to avoid mutating the global
        locs = dict(location_data)

        # Hardcoded coordinates map (Name -> (lat, lon)) provided by user
        COORDS_MAP = {
            "Chisinau": (47.0166, 28.8499),
            "Orhei": (47.3792, 28.8239),
            "Tiraspol": (46.8406, 29.6083),
            "Balti": (47.7618, 27.919),
            "Soroca": (48.1565, 28.2995),
            "Cricova": (47.1352, 28.7611),
            "Vadul lui Voda": (47.1287, 29.0838),
            "Comrat": (46.3005, 28.6601),
            "Cahul": (45.9084, 28.196),
            "Edinet": (48.1718, 27.3079),
            "Ungheni": (47.2106, 27.8006),
            "Rezina": (47.7481, 29.0444),
            "Hincesti": (46.8317, 28.5878),
            "Floresti": (47.8917, 28.2992),
            "Stefan Voda": (46.5156, 29.6633),
        }

        # Extract numeric consumption values robustly (support numeric, string, or dict forms)
        consumptions = []
        for v in locs.values():
            try:
                if isinstance(v, (int, float)):
                    val = float(v)
                elif isinstance(v, str):
                    tmp = v.replace(",", "").replace(" ", "")
                    val = float(tmp)
                elif isinstance(v, dict):
                    raw = v.get("consumption", 0)
                    if raw is None:
                        raw = 0
                    if isinstance(raw, str):
                        raw = raw.replace(",", "").replace(" ", "")
                    val = float(raw)
                else:
                    # try coercion
                    val = float(v)
            except Exception:
                val = 0.0
            consumptions.append(val)

        min_c = min(consumptions) if consumptions else 0.0
        max_c = max(consumptions) if consumptions else 0.0

        # Color mapping: norm 0 -> (0,255,0) green, 0.5 -> (255,255,0) yellow, 1 -> (255,0,0) red.
        # We'll use a simple linear blend: r = 255*norm, g = 255*(1-norm), b = 0.
        def get_color_from_value(cons_value: float):
            try:
                cons_value = float(cons_value or 0.0)
            except Exception:
                cons_value = 0.0

            if max_c > min_c:
                norm = (cons_value - min_c) / (max_c - min_c)
            else:
                # all equal: choose a greenish color (low usage)
                norm = 0.0

            # Clamp to [0,1]
            norm = max(0.0, min(1.0, norm))

            r = int(round(255 * norm))
            g = int(round(255 * (1.0 - norm)))
            b = 0
            return (r, g, b)

        result = {}
        for city, item in locs.items():
            try:
                # Handle two possible shapes for `item`:
                # 1) a numeric value (e.g., {'Balti': 1249688.0})
                # 2) a dict with keys like 'consumption' and 'coordonates' or 'coordinates'
                if isinstance(item, (int, float)):
                    cons_val = float(item)
                    coords_raw = None
                elif isinstance(item, str):
                    # numeric stored as string
                    try:
                        cons_val = float(item.replace(",", "").replace(" ", ""))
                    except Exception:
                        cons_val = 0.0
                    coords_raw = None
                elif isinstance(item, dict):
                    raw = item.get("consumption", 0)
                    if raw is None:
                        raw = 0
                    if isinstance(raw, str):
                        raw = raw.replace(",", "").replace(" ", "")
                    try:
                        cons_val = float(raw)
                    except Exception:
                        cons_val = 0.0
                    coords_raw = item.get("coordonates", item.get("coordinates", None))
                else:
                    # unknown type
                    try:
                        cons_val = float(item)
                    except Exception:
                        cons_val = 0.0
                    coords_raw = None

                # coordinates resolution: if coords_raw provided and iterable, convert to tuple of floats
                if coords_raw is not None:
                    try:
                        coords = tuple(float(x) for x in coords_raw)
                    except Exception:
                        coords = COORDS_MAP.get(city, (0.0, 0.0))
                else:
                    # fall back to hardcoded coordinates map if available
                    coords = COORDS_MAP.get(city, (0.0, 0.0))

                # compute color based on consumption value
                color_tuple = get_color_from_value(cons_val)

                result[city] = {
                    "consumption": float(cons_val),
                    "color": color_tuple,
                    "coordonates": coords,
                    "coordinates": coords,
                }
            except Exception as e:
                print(f"Error processing city {city}: {e}")

        return result

if __name__ == '__main__':
    print(get_series_country("Hincesti"))
