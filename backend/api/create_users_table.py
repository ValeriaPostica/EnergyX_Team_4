from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Enum
import enum

#Database connection
engine = create_engine("postgresql://postgres:11111@localhost:5433/postgres")
metadata = MetaData()

#define users' roles
class UserRole(enum.Enum):
	PROVIDER = "provider"
	CONSUMER = "consumer"

#create users tables
users_tables = Table(
	'users',
	metadata,
	Column('id', Integer, primary_key=True, autoincrement=True),
	Column('username', String(50), unique=True, nullable=False),
	Column('email', String(100), unique=True, nullable=False),
	Column('password', String(255), nullable=False),
	Column('role', String(20), nullable=False),
	Column('smart_meter_id', String(50), nullable=True),
	schema='public'
)

#creating the Table
print("Creating the table...")
metadata.create_all(engine)
print("Table created successfully!")

#verify
from sqlalchemy import inspect
insp = inspect(engine)
if 'users' in insp.get_table_names(schema='public'):
	print("\n Verified: 'users' table exists")
	cols = insp.get_columns('users', schema='public')
	print("\nColumns:")
	for c in cols:
		print(f"  - {c['name']}: {c['type']}")
else:
	print("Something went wrong, table NOT FOUND")