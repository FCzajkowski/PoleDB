import sqlite3
import os
from rich.console import Console
from rich.align import Align
import readchar
import platform
import shutil  # To get terminal size

console = Console()

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

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
        return

    if did_it_log:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        # Menu options: "CREATE NEW TABLE" + existing tables
        options = ["CREATE NEW TABLE"] + tables
        selected = 0

        while True:
            clear_screen()
            term_width, term_height = shutil.get_terminal_size()

            # Build menu text
            menu_lines = [f"Connected to [#CC22BB on black]{database_name}.db\n [/#CC22BB on black]"]
            for i, option in enumerate(options):
                if i == selected:
                    # Highlight selected option
                    menu_lines.append(f"[black on #E0F7FA]> {option} <[/black on #E0F7FA]")
                else:
                    menu_lines.append(option)

            menu_text = "\n".join(menu_lines)

            # Calculate vertical padding to center
            vertical_padding = max((term_height - len(menu_lines)) // 2, 0)
            padded_menu = "\n" * vertical_padding + menu_text

            # Center horizontally using Rich Align
            console.print(Align.center(padded_menu))

            key = readchar.readkey()
            if key == readchar.key.UP:
                selected = (selected - 1) % len(options)
            elif key == readchar.key.DOWN:
                selected = (selected + 1) % len(options)
            elif key == readchar.key.ENTER:
                pass  # Do nothing for now
            elif key in [readchar.key.CTRL_C, readchar.key.CTRL_X, readchar.key.CTRL_Z]:
                clear_screen()
                console.print("Exiting...")
                break

if __name__ == "__main__":
    db_name = input("Enter database name (without .db): ")
    main_loop(db_name)
