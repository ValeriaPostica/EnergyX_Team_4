from sqlalchemy import create_engine, inspect, text

engine = create_engine("postgresql://postgres:11111@localhost:5433/postgres")

# Check what tables exist
insp = inspect(engine)
schemas = insp.get_schema_names()

print("=== ALL TABLES ===")
for schema in schemas:
    tables = insp.get_table_names(schema=schema)
    for table in tables:
        print(f"{schema}.{table}")

# Check if there's a users table
print("\n=== LOOKING FOR USERS TABLE ===")
if 'users' in insp.get_table_names(schema='public'):
    print("Found 'users' table!")
    cols = insp.get_columns('users', schema='public')
    print("Columns:")
    for c in cols:
        print(f"  - {c['name']}: {c['type']}")
else:
    print("No 'users' table found - you'll need to create it!")