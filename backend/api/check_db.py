from sqlalchemy import create_engine, inspect, text
from get_db_string import get_db_string



engine = create_engine(get_db_string())
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