
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:11111@localhost:5433/postgres")
engine = create_engine(DATABASE_URL)

def check_data():
    print(f"Connecting to {DATABASE_URL}")
    try:
        with engine.connect() as conn:
            # 1. Check locations
            print("\n--- Locations ---")
            result = conn.execute(text("SELECT * FROM public.locations"))
            locations = result.fetchall()
            for loc in locations:
                print(loc)
                
            # 2. Check contour count per location
            print("\n--- Data Count per Location ---")
            sql = text("""
                SELECT l.name, COUNT(cd.contour_id) 
                FROM public.locations l
                JOIN public.contour c ON l.location_id = c.location_id
                JOIN public.contour_data cd ON c.contour_id = cd.contour_id
                GROUP BY l.name
            """)
            result = conn.execute(sql).fetchall()
            for row in result:
                print(row)

            # 3. Check specific query for Balti
            print("\n--- Query Test for Balti ---")
            country = "Balti"
            table = "public.contour c JOIN public.locations l ON c.location_id = l.location_id JOIN public.contour_data cd ON c.contour_id = cd.contour_id"
            sql_query = text(f"SELECT COUNT(*) FROM {table} WHERE date_part('minute', clock) = 0 AND l.name = :country")
            count = conn.execute(sql_query, {"country": country}).scalar()
            print(f"Rows for {country} (minute=0): {count}")

            # 4. Deep Dive
            print("\n--- Deep Dive ---")
            # Check total rows in contour_data
            total_rows = conn.execute(text("SELECT COUNT(*) FROM public.contour_data")).scalar()
            print(f"Total rows in contour_data: {total_rows}")

            # Sample rows from contour_data
            print("Sample rows from contour_data:")
            sample = conn.execute(text("SELECT * FROM public.contour_data LIMIT 5")).fetchall()
            for row in sample:
                print(row)

            # Check contour table
            print("Contour table (first 5):")
            contours = conn.execute(text("SELECT * FROM public.contour LIMIT 5")).fetchall()
            for row in contours:
                print(row)

            # 5. Mismatch Investigation
            print("\n--- Mismatch Investigation ---")
            # Get some contour_ids from contour_data
            cd_ids = conn.execute(text("SELECT DISTINCT contour_id FROM public.contour_data LIMIT 10")).fetchall()
            cd_ids = [row[0] for row in cd_ids]
            print(f"Sample contour_ids from contour_data: {cd_ids}")

            # Check if these exist in contour table
            if cd_ids:
                placeholders = ','.join([':id' + str(i) for i in range(len(cd_ids))])
                params = {f'id{i}': id_val for i, id_val in enumerate(cd_ids)}
                sql = text(f"SELECT contour_id FROM public.contour WHERE contour_id IN ({placeholders})")
                found_ids = conn.execute(sql, params).fetchall()
                print(f"Found in contour table: {found_ids}")
            
            # Get some contour_ids from contour table
            c_ids = conn.execute(text("SELECT contour_id FROM public.contour LIMIT 10")).fetchall()
            c_ids = [row[0] for row in c_ids]
            print(f"Sample contour_ids from contour table: {c_ids}")

            # Check if these exist in contour_data table
            if c_ids:
                placeholders = ','.join([':id' + str(i) for i in range(len(c_ids))])
                params = {f'id{i}': id_val for i, id_val in enumerate(c_ids)}
                sql = text(f"SELECT DISTINCT contour_id FROM public.contour_data WHERE contour_id IN ({placeholders})")
                found_in_data = conn.execute(sql, params).fetchall()
                print(f"Found in contour_data table: {found_in_data}")

            # 6. Link Investigation (Contour -> Location)
            print("\n--- Link Investigation (Contour -> Location) ---")
            # Get location_ids from contour table for the contours that have data
            if cd_ids:
                placeholders = ','.join([':id' + str(i) for i in range(len(cd_ids))])
                params = {f'id{i}': id_val for i, id_val in enumerate(cd_ids)}
                sql = text(f"SELECT contour_id, location_id FROM public.contour WHERE contour_id IN ({placeholders})")
                c_locs = conn.execute(sql, params).fetchall()
                print(f"Location IDs for sample contours: {c_locs}")
                
                # Check if these location_ids exist in locations table
                loc_ids = [row[1] for row in c_locs if row[1] is not None]
                if loc_ids:
                    # distinct
                    loc_ids = list(set(loc_ids))
                    print(f"Distinct Location IDs to check: {loc_ids}")
                    
                    placeholders_l = ','.join([':id' + str(i) for i in range(len(loc_ids))])
                    params_l = {f'id{i}': id_val for i, id_val in enumerate(loc_ids)}
                    sql = text(f"SELECT location_id, name FROM public.locations WHERE location_id IN ({placeholders_l})")
                    found_locs = conn.execute(sql, params_l).fetchall()
                    print(f"Found in locations table: {found_locs}")
                else:
                    print("No location_ids found in sample contours (or all None).")

            # 7. Check Balti specifically in contour table
            print("\n--- Balti Check ---")
            # Get Balti location_id
            balti_id = conn.execute(text("SELECT location_id FROM public.locations WHERE name = 'Balti'")).scalar()
            print(f"Balti Location ID: {balti_id}")
            
            if balti_id:
                # Check if any contour has this location_id
                c_count = conn.execute(text(f"SELECT COUNT(*) FROM public.contour WHERE location_id = {balti_id}")).scalar()
                print(f"Contours with Balti location_id: {c_count}")
                
                if c_count > 0:
                    # Check if these contours have data
                    sql = text(f"""
                        SELECT COUNT(*) 
                        FROM public.contour_data cd
                        JOIN public.contour c ON cd.contour_id = c.contour_id
                        WHERE c.location_id = {balti_id}
                    """)
                    data_count = conn.execute(sql).scalar()
                    print(f"Data rows for Balti contours: {data_count}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
