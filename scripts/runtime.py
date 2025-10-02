import sqlite3
import os

def main_loop(database_name: str):
    did_it_log = False
    current_dir = os.getcwd()
    db_path = os.path.join(current_dir, f"{database_name}.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        did_it_log = True
    except sqlite3.Error as e:
        print(f"Database did NOT load: {e}")

    if did_it_log:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables in {database_name}.db: {tables}")

        print(tables)
        while True:
            user_input = input(f"{database_name}>>")
            user_input = user_input.lower()
            if user_input in ["exit", "break", "^x", "^z"]:
                break
            
            else:
                pass