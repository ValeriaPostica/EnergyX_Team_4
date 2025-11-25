
import os
import psycopg2

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 
def load_migrations():
    MIGRATIONS_FOLDER=os.path.join(ROOT_DIR, "..", "..", "db", "migrations")

    try:
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="11111",
            port="5433"
        )
        
    except Exception as e:
        print(e)
        print("\n Cannot connect to the database")
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
            --CREATE SCHEMA IF NOT EXISTS public;
            --SET search_path TO public;
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
        try:
            cur.execute("INSERT INTO migrations.applied (migration,val) VALUES (%s,%s)", (os.path.basename(m),file_content,))
            cur.execute(file_content)
            conn.commit()
        except Exception as e:
            print(f"Error applying migration: {e}")
    conn.close()

if __name__ == "__main__":
    load_migrations()