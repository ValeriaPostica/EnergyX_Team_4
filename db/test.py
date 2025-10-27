from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:11111@localhost:5433/postgres")
table_contour = "interpolated.contour"
table_locations = "interpolated.locations"
table_contour_data = "interpolated.contour_data"

with engine.connect() as conn:
    # qualify columns with table aliases to avoid ambiguous column references
    q = text(f"""
    SELECT c.contour_id AS contour_id,
        l.name       AS location_name,
        cd.energy_import  AS energy_import,
        cd.energy_export  AS energy_export,
        cd.clock      AS clock
    FROM interpolated.contour c
    JOIN interpolated.locations l ON c.location_id = l.location_id
    JOIN interpolated.contour_data cd ON c.contour_id = cd.contour_id
    LIMIT 100
    """)
    res = conn.execute(q)
    cols = res.keys()

    # Print column names as a header (first row)
    header = " ".join(cols)
    print(header)
    if res is None:
        print("No rows returned.")
    else:
        # Print only the values (no dict), in the same order as the header
        for values in res:
            print(values)