import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
import psycopg2
import sys


# Take the params from env vars
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5433')           
DB_NAME = os.getenv('DB_NAME', 'postgres')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '11111')


ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 
MIGRATIONS_FOLDER=os.path.join(ROOT_DIR, "migrations")


def load_migrations():

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        
    except Exception as e:
        print(e)
        print("\n Cannot connect to the database")
        exit(1)
        return
    migration_files = []
    for item in os.listdir(MIGRATIONS_FOLDER):
        item_p = os.path.join(MIGRATIONS_FOLDER, item)
        if os.path.isfile(item_p) and str(item_p).endswith(".sql"):
            migration_files.append(item_p)
    
    migration_files = list(map(lambda x: str(x), migration_files))
    cur = conn.cursor()
    cur.execute('''
            CREATE SCHEMA IF NOT EXISTS migrations;
            CREATE TABLE IF NOT EXISTS migrations.applied (
                migration TEXT,
                val TEXT
            );
            -- CREATE SCHEMA IF NOT EXISTS interpolated;
            -- SET search_path TO interpolated;
                ''')
    cur.execute("SELECT migration FROM migrations.applied ORDER BY migration")
    applied_migs = cur.fetchall()
    migration_files = sorted(list(set(migration_files) - set(map(lambda x: str(os.path.join(MIGRATIONS_FOLDER, x[0])), applied_migs))))
    conn.commit()
    print("migrations that are going to be applied",migration_files)
    for m in migration_files:
        print("will be applied",m)
        cur = conn.cursor()
        file_content = open(m).read()
        cur.execute("INSERT INTO migrations.applied (migration,val) VALUES (%s,%s)", (os.path.basename(m),file_content,))
        cur.execute(file_content)
        conn.commit()
    conn.close()


def write_to_db(engine, df, table_name):
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        schema='public',
        index=False,
        chunksize=1000
    )



def process_data():
    csv_data = pd.read_csv('v_data.csv')
    csv_data['location_id'] = csv_data.groupby('name').ngroup() + 1

    # 1. Process contour table
    contour = csv_data.drop_duplicates(['contour_id', 'fuel_coefficient', 'location_id'])
    contour = contour[['contour_id', 'fuel_coefficient', 'location_id']].sort_values('contour_id')

    # 2. Process location table
    locations = csv_data.drop_duplicates(['location_id', 'name', 'lat', 'lon'])
    locations = locations[['location_id', 'name', 'lat', 'lon']].sort_values('name')

    # 3. Process contour_data table
    contour_data = csv_data[['contour_id', 'energy_export', 'energy_import', 'clock']].copy()
    contour_data['clock'] = pd.to_datetime(contour_data['clock'])
    contour_data = contour_data.sort_values(['contour_id', 'clock'])

    # --- FIX START: Avoiding SettingWithCopyWarning ---
    # Create a clean, independent copy for processing
    import_export = contour_data[['energy_import', 'energy_export']].copy()

    # Identify zero-lines and replace with NaN for interpolation
    mask = (import_export['energy_import'] == 0) & (import_export['energy_export'] == 0)
    import_export.loc[mask, ['energy_import', 'energy_export']] = np.nan

    # Modern interpolation and fillna
    import_export['energy_import'] = import_export['energy_import'].interpolate(method='linear')
    import_export['energy_export'] = import_export['energy_export'].interpolate(method='linear')
    
    # Use bfill/ffill directly as .fillna(method=...) is deprecated
    import_export = import_export.bfill().ffill()
    # --- FIX END ---

    # Map processed values back to the main table
    contour_data['energy_import'] = import_export['energy_import'].astype(int)
    contour_data['energy_export'] = import_export['energy_export'].astype(int)

    # 4. Save to cache (Using Feather for max speed as discussed)
    locations.to_parquet('locations.parquet')
    contour.to_parquet('contour.parquet')
    contour_data.to_parquet('contour_data.parquet')

def load_data():

    print("Reading parquet files...")
    try:
        locations = pd.read_parquet('locations.parquet')
        contour = pd.read_parquet('contour.parquet')
        contour_data = pd.read_parquet('contour_data.parquet')
    except Exception as e:
        print(f"Error reading parquet files: {e}")
        exit(1)
    
    print("Parquet files read successfully.")

    print("Migrating database...")
    try:
        load_migrations()
    except Exception as e:
        print(f"Error loading migrations: {e}")
        exit(1)
    
    print("Creating database engine...")
    # Create the SQLAlchemy engine
    engine_string = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(engine_string)

    print("Writing data to database...")
    # Write dataframes to the database
    write_to_db(engine, locations, 'locations')
    write_to_db(engine, contour, 'contour')
    write_to_db(engine, contour_data, 'contour_data')
    print("Data loading complete.")

def main():
    #determine which mode to run based on the arguments load, calc
    # If the second argument is calc run process_data
    if len(sys.argv) > 1 and sys.argv[1] == 'calc':
        process_data()
    else:
        FLAG_FILE = "/app/.init_done"

        if os.path.exists(FLAG_FILE):
            print("Database already initialized. Skipping.")
            sys.exit(0)

        load_data()
        print("Database initialization complete.")
        with open(FLAG_FILE, "w") as f:
            f.write("done")

if __name__ == "__main__":
    main()