from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:11111@localhost:5433/postgres")
table = "contour_data"
with engine.connect() as conn:
    q = text(f"SELECT * FROM {table} WHERE contour_id = 14101503")  # or use SQLAlchemy Table reflection for safety
    rows = conn.execute(q).fetchall()
    print("Rows:", len(rows))
    if rows:
        for row in rows:
            print(row)