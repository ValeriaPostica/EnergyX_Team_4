from sqlalchemy import create_engine, text
import sys
from typing import Optional

# Usage: python series.py <contour_id>
engine = create_engine("postgresql://postgres:11111@localhost:5433/postgres")


def fetch_hourly_imports(contour_id: int, day: Optional[int] = None, schema: Optional[str] = "interpolated"):
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

def general_info(schema: Optional[str] = "interpolated"):
    table = f"{schema}.contour_data" if schema else "contour_data"
    sql = text(
        f"SELECT energy_import FROM {table} LIMIT 841"
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

    return current_usage, int(number_of_contours*5)

if __name__ == '__main__':
    print(general_info())
