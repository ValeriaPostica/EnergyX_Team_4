
import os
import random
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:11111@localhost:5433/postgres")
engine = create_engine(DATABASE_URL)

def assign_locations():
    print(f"Connecting to {DATABASE_URL}")
    try:
        with engine.connect() as conn:
            # 1. Get contours with missing location_id
            print("Fetching contours with missing location_id...")
            contours = conn.execute(text("SELECT contour_id FROM public.contour WHERE location_id IS NULL")).fetchall()
            contour_ids = [r[0] for r in contours]
            print(f"Found {len(contour_ids)} contours without location.")

            if not contour_ids:
                print("No contours to update.")
                return

            # 2. Get all location IDs
            print("Fetching locations...")
            locations = conn.execute(text("SELECT location_id FROM public.locations")).fetchall()
            location_ids = [r[0] for r in locations]
            print(f"Found {len(location_ids)} locations.")

            if not location_ids:
                print("No locations found! Cannot assign.")
                return

            # 3. Assign locations
            print("Assigning locations...")
            # Use round-robin to distribute evenly
            updates = []
            for i, cid in enumerate(contour_ids):
                loc_id = location_ids[i % len(location_ids)]
                updates.append({"cid": cid, "lid": loc_id})

            # 4. Execute updates in batches
            batch_size = 1000
            total_updated = 0
            
            print(f"Starting updates for {len(updates)} contours...")
            
            # We can use executemany logic or just a loop with transactions
            # SQLAlchemy's execute with list of dicts does executemany
            
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i+batch_size]
                conn.execute(
                    text("UPDATE public.contour SET location_id = :lid WHERE contour_id = :cid"),
                    batch
                )
                conn.commit()
                total_updated += len(batch)
                print(f"Updated {total_updated}/{len(updates)}")

            print("Done!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    assign_locations()
