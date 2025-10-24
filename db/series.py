from sqlalchemy import create_engine, text
import sys
from typing import Optional

# Usage: python series.py <contour_id>
engine = create_engine("postgresql://postgres:11111@localhost:5433/postgres")


def fetch_hourly_imports(contour_id: int, day: int, schema: Optional[str] = "interpolated"):
    """Return rows (contour_id, clock, energy_import) for the given contour_id
    where the timestamp is at whole hours (minute = 0). Results are ordered by clock ascending.
    """
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
    return [j - i for i, j in zip(series[:-1], series[1:])]

def main():
    if len(sys.argv) < 2:
        print("Usage: python series.py <contour_id>")
        sys.exit(1)
    try:
        cid = int(sys.argv[1])
    except ValueError:
        print("contour_id must be an integer")
        sys.exit(1)

    rows = fetch_hourly_imports(cid, day=7)
    print(f"Found {len(rows)} rows for contour_id={cid} at whole hours")
    series = []
    for r in rows:
        print(r[0], r[1], r[2])
        series.append(r[2])

    print("Series:", series)
    diffs = diff(series)
    print("First differences:", diffs)

if __name__ == '__main__':
    main()
