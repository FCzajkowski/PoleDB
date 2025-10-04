import sqlite3, os, readchar, platform, shutil
from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich.panel import Panel

console = Console()

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def create_new_table(cursor, conn):
    """Interactive table creation interface"""
    clear_screen()
    
    # Step 1: Get table name
    console.print(Panel("[bold cyan]Create New Table[/bold cyan]", expand=False))
    table_name = console.input("\n[yellow]Enter table name:[/yellow] ").strip()
    
    if not table_name:
        console.print("[red]Table name cannot be empty![/red]")
        input("\nPress Enter to continue...")
        return
    
    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if cursor.fetchone():
        console.print(f"[red]Table '{table_name}' already exists![/red]")
        input("\nPress Enter to continue...")
        return
    
    # Step 2: Define columns
    columns = []
    column_counter = 1
    
    while True:
        clear_screen()
        console.print(Panel(f"[bold cyan]Creating Table: {table_name}[/bold cyan]", expand=False))
        
        # Display current columns
        if columns:
            console.print("\n[bold green]Current Columns:[/bold green]")
            for idx, col in enumerate(columns, 1):
                pk_marker = " [yellow](PRIMARY KEY)[/yellow]" if col['pk'] else ""
                nn_marker = " [cyan](NOT NULL)[/cyan]" if col['not_null'] else ""
                unique_marker = " [magenta](UNIQUE)[/magenta]" if col['unique'] else ""
                default_marker = f" [dim](DEFAULT: {col['default']})[/dim]" if col['default'] else ""
                console.print(f"  {idx}. [bold]{col['name']}[/bold] - {col['type']}{pk_marker}{nn_marker}{unique_marker}{default_marker}")
        
        console.print("\n[dim]Options:[/dim]")
        console.print("  [1] Add column")
        console.print("  [2] Remove last column")
        console.print("  [3] Finish and create table")
        console.print("  [4] Cancel")
        
        choice = console.input("\n[yellow]Choose option:[/yellow] ").strip()
        
        if choice == "1":
            # Add column
            clear_screen()
            console.print(Panel(f"[bold cyan]Add Column #{column_counter}[/bold cyan]", expand=False))
            
            col_name = console.input("\n[yellow]Column name:[/yellow] ").strip()
            if not col_name:
                console.print("[red]Column name cannot be empty![/red]")
                input("\nPress Enter to continue...")
                continue
            
            # Column type
            console.print("\n[bold]Select data type:[/bold]")
            types = ["INTEGER", "TEXT", "REAL", "BLOB", "NUMERIC"]
            for i, t in enumerate(types, 1):
                console.print(f"  [{i}] {t}")
            
            type_choice = console.input("\n[yellow]Choose type (1-5):[/yellow] ").strip()
            try:
                col_type = types[int(type_choice) - 1]
            except (ValueError, IndexError):
                col_type = "TEXT"
            
            # Primary Key
            is_pk = console.input("\n[yellow]Primary Key? (y/n):[/yellow] ").strip().lower() == 'y'
            
            # Not Null
            is_not_null = False
            if not is_pk:  # PK is automatically NOT NULL
                is_not_null = console.input("[yellow]NOT NULL? (y/n):[/yellow] ").strip().lower() == 'y'
            
            # Unique
            is_unique = False
            if not is_pk:  # PK is automatically UNIQUE
                is_unique = console.input("[yellow]UNIQUE? (y/n):[/yellow] ").strip().lower() == 'y'
            
            # Default value
            default_val = ""
            if not is_pk:
                default_input = console.input("[yellow]Default value (leave empty for none):[/yellow] ").strip()
                if default_input:
                    default_val = default_input
            
            columns.append({
                'name': col_name,
                'type': col_type,
                'pk': is_pk,
                'not_null': is_not_null or is_pk,
                'unique': is_unique or is_pk,
                'default': default_val
            })
            column_counter += 1
            
        elif choice == "2":
            # Remove last column
            if columns:
                removed = columns.pop()
                console.print(f"[green]Removed column: {removed['name']}[/green]")
                input("\nPress Enter to continue...")
            else:
                console.print("[red]No columns to remove![/red]")
                input("\nPress Enter to continue...")
                
        elif choice == "3":
            # Create table
            if not columns:
                console.print("[red]Table must have at least one column![/red]")
                input("\nPress Enter to continue...")
                continue
            
            # Build CREATE TABLE statement
            col_definitions = []
            for col in columns:
                col_def = f"{col['name']} {col['type']}"
                if col['pk']:
                    col_def += " PRIMARY KEY"
                if col['not_null'] and not col['pk']:
                    col_def += " NOT NULL"
                if col['unique'] and not col['pk']:
                    col_def += " UNIQUE"
                if col['default']:
                    # Add quotes for TEXT/BLOB types
                    if col['type'] in ['TEXT', 'BLOB']:
                        col_def += f" DEFAULT '{col['default']}'"
                    else:
                        col_def += f" DEFAULT {col['default']}"
                col_definitions.append(col_def)
            
            sql = f"CREATE TABLE {table_name} ({', '.join(col_definitions)})"
            
            # Show SQL and confirm
            clear_screen()
            console.print(Panel("[bold green]Ready to Create Table[/bold green]", expand=False))
            console.print(f"\n[dim]SQL:[/dim]\n{sql}\n")
            
            confirm = console.input("[yellow]Create this table? (y/n):[/yellow] ").strip().lower()
            if confirm == 'y':
                try:
                    cursor.execute(sql)
                    conn.commit()
                    console.print(f"\n[bold green]✓ Table '{table_name}' created successfully![/bold green]")
                except sqlite3.Error as e:
                    console.print(f"\n[red]Error creating table: {e}[/red]")
                input("\nPress Enter to continue...")
                return
            
        elif choice == "4":
            # Cancel
            console.print("[yellow]Table creation cancelled.[/yellow]")
            input("\nPress Enter to continue...")
            return

def row_editing_menu(cursor, conn, table_name):
    """Handle row editing operations"""
    options = ["Insert Row", "Edit Row", "Delete Row", "Truncate", "Back"]
    selected = 0
    
    while True:
        clear_screen()
        console.print(Panel(f"[bold cyan]Row Editing - {table_name}[/bold cyan]", expand=False))
        console.print()
        
        for i, option in enumerate(options):
            if i == selected:
                console.print(f"[black on #E0F7FA]> {option} <[/black on #E0F7FA]")
            else:
                console.print(f"  {option}")
        
        console.print("\n[dim]Use arrow keys to navigate, ENTER to select, ESC to go back[/dim]")
        
        key = readchar.readkey()
        if key == readchar.key.UP:
            selected = (selected - 1) % len(options)
        elif key == readchar.key.DOWN:
            selected = (selected + 1) % len(options)
        elif key == readchar.key.ENTER:
            if selected == 4:  # Back
                break
            elif selected == 0:  # Insert Row
                insert_row(cursor, conn, table_name)
            elif selected == 1:  # Edit Row
                edit_row(cursor, conn, table_name)
            elif selected == 2:  # Delete Row
                delete_row(cursor, conn, table_name)
            elif selected == 3:  # Truncate
                truncate_table(cursor, conn, table_name)
        elif key == readchar.key.ESC:
            break

def insert_row(cursor, conn, table_name):
    """Insert a new row into the table"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Insert Row - {table_name}[/bold cyan]", expand=False))
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    
    values = []
    col_names = []
    
    for col in columns_info:
        col_name = col[1]
        col_type = col[2]
        not_null = col[3]
        default_val = col[4]
        is_pk = col[5]
        
        # Skip auto-increment primary keys
        if is_pk and col_type.upper() == "INTEGER":
            console.print(f"[dim]Skipping auto-increment PK: {col_name}[/dim]")
            continue
        
        col_names.append(col_name)
        
        prompt = f"[yellow]{col_name}[/yellow] ({col_type})"
        if default_val:
            prompt += f" [dim](default: {default_val})[/dim]"
        if not_null:
            prompt += " [red]*required[/red]"
        prompt += ": "
        
        value = console.input(prompt).strip()
        
        if not value and default_val:
            values.append(None)  # Use default
        elif not value and not_null:
            console.print("[red]This field is required![/red]")
            input("\nPress Enter to continue...")
            return
        else:
            values.append(value if value else None)
    
    # Build INSERT statement
    placeholders = ",".join(["?" for _ in values])
    col_list = ",".join(col_names)
    
    try:
        cursor.execute(f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})", values)
        conn.commit()
        console.print("\n[bold green]✓ Row inserted successfully![/bold green]")
    except sqlite3.Error as e:
        console.print(f"\n[red]Error inserting row: {e}[/red]")
    
    input("\nPress Enter to continue...")

def edit_row(cursor, conn, table_name):
    """Edit an existing row"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Edit Row - {table_name}[/bold cyan]", expand=False))
    
    # Get primary key column
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    pk_col = None
    for col in columns_info:
        if col[5]:  # is_pk
            pk_col = col[1]
            break
    
    if not pk_col:
        console.print("[red]Table has no primary key. Cannot edit rows safely.[/red]")
        input("\nPress Enter to continue...")
        return
    
    # Show recent rows
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
    rows = cursor.fetchall()
    console.print("\n[bold]Recent rows:[/bold]")
    for row in rows:
        console.print(f"  {row}")
    
    row_id = console.input(f"\n[yellow]Enter {pk_col} value to edit:[/yellow] ").strip()
    
    # Fetch the row
    cursor.execute(f"SELECT * FROM {table_name} WHERE {pk_col} = ?", (row_id,))
    row = cursor.fetchone()
    
    if not row:
        console.print(f"[red]No row found with {pk_col} = {row_id}[/red]")
        input("\nPress Enter to continue...")
        return
    
    console.print("\n[green]Current values:[/green]")
    for col, val in zip([c[1] for c in columns_info], row):
        console.print(f"  {col}: {val}")
    
    # Get new values
    console.print("\n[dim]Enter new values (press Enter to keep current value):[/dim]")
    new_values = {}
    for col in columns_info:
        col_name = col[1]
        if col[5]:  # Skip PK
            continue
        
        current_val = row[col[0]]
        new_val = console.input(f"[yellow]{col_name}[/yellow] (current: {current_val}): ").strip()
        
        if new_val:
            new_values[col_name] = new_val
    
    if not new_values:
        console.print("[yellow]No changes made.[/yellow]")
        input("\nPress Enter to continue...")
        return
    
    # Build UPDATE statement
    set_clause = ", ".join([f"{col} = ?" for col in new_values.keys()])
    values = list(new_values.values()) + [row_id]
    
    try:
        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {pk_col} = ?", values)
        conn.commit()
        console.print("\n[bold green]✓ Row updated successfully![/bold green]")
    except sqlite3.Error as e:
        console.print(f"\n[red]Error updating row: {e}[/red]")
    
    input("\nPress Enter to continue...")

def delete_row(cursor, conn, table_name):
    """Delete a row from the table"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Delete Row - {table_name}[/bold cyan]", expand=False))
    
    # Get primary key column
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    pk_col = None
    for col in columns_info:
        if col[5]:
            pk_col = col[1]
            break
    
    if not pk_col:
        console.print("[red]Table has no primary key. Cannot delete rows safely.[/red]")
        input("\nPress Enter to continue...")
        return
    
    # Show recent rows
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
    rows = cursor.fetchall()
    console.print("\n[bold]Recent rows:[/bold]")
    for row in rows:
        console.print(f"  {row}")
    
    row_id = console.input(f"\n[yellow]Enter {pk_col} value to delete:[/yellow] ").strip()
    
    confirm = console.input(f"[red]Are you sure you want to delete row with {pk_col} = {row_id}? (y/n):[/red] ").strip().lower()
    
    if confirm == 'y':
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE {pk_col} = ?", (row_id,))
            conn.commit()
            console.print("\n[bold green]✓ Row deleted successfully![/bold green]")
        except sqlite3.Error as e:
            console.print(f"\n[red]Error deleting row: {e}[/red]")
    else:
        console.print("[yellow]Deletion cancelled.[/yellow]")
    
    input("\nPress Enter to continue...")

def truncate_table(cursor, conn, table_name):
    """Delete all rows from the table"""
    clear_screen()
    console.print(Panel(f"[bold red]Truncate Table - {table_name}[/bold red]", expand=False))
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    console.print(f"\n[yellow]This will delete all {row_count} rows from {table_name}![/yellow]")
    confirm = console.input("[red]Type 'DELETE ALL' to confirm:[/red] ").strip()
    
    if confirm == "DELETE ALL":
        try:
            cursor.execute(f"DELETE FROM {table_name}")
            conn.commit()
            console.print("\n[bold green]✓ Table truncated successfully![/bold green]")
        except sqlite3.Error as e:
            console.print(f"\n[red]Error truncating table: {e}[/red]")
    else:
        console.print("[yellow]Truncation cancelled.[/yellow]")
    
    input("\nPress Enter to continue...")

def search_filter(cursor, table_name):
    """Search and filter table data"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Search/Filter - {table_name}[/bold cyan]", expand=False))
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    console.print("\n[bold]Available columns:[/bold]")
    for col in columns:
        console.print(f"  • {col}")
    
    column = console.input("\n[yellow]Enter column name:[/yellow] ").strip()
    query = console.input("[yellow]Enter query (e.g., LIKE '%abc%', = 'value', > 100):[/yellow] ").strip()
    
    try:
        sql = f"SELECT * FROM {table_name} WHERE {column} {query}"
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        if not rows:
            console.print("\n[yellow]No matching rows found.[/yellow]")
        else:
            # Create Rich table
            rich_table = Table(title=f"[bold green]Search Results ({len(rows)} rows)[/bold green]")
            
            for col in columns:
                rich_table.add_column(f"[bold cyan]{col}[/bold cyan]", style="white")
            
            for row in rows:
                rich_table.add_row(*[str(cell) for cell in row])
            
            console.print()
            console.print(rich_table)
    
    except sqlite3.Error as e:
        console.print(f"\n[red]Error executing query: {e}[/red]")
    
    input("\nPress Enter to continue...")

def table_info(cursor, table_name):
    """Display table information"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Table Info - {table_name}[/bold cyan]", expand=False))
    
    # Column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    
    console.print("\n[bold green]Columns:[/bold green]")
    info_table = Table()
    info_table.add_column("Name", style="cyan")
    info_table.add_column("Type", style="yellow")
    info_table.add_column("Not Null", style="magenta")
    info_table.add_column("Default", style="white")
    info_table.add_column("Primary Key", style="red")
    
    for col in columns_info:
        info_table.add_row(
            col[1],  # name
            col[2],  # type
            "YES" if col[3] else "NO",  # not null
            str(col[4]) if col[4] else "NULL",  # default
            "YES" if col[5] else "NO"  # pk
        )
    
    console.print(info_table)
    
    # Row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    console.print(f"\n[bold]Row Count:[/bold] {row_count}")
    
    # Index information
    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes = cursor.fetchall()
    
    if indexes:
        console.print("\n[bold green]Indexes:[/bold green]")
        for idx in indexes:
            console.print(f"  • {idx[1]} (unique: {idx[2]})")
    else:
        console.print("\n[dim]No indexes defined.[/dim]")
    
    input("\nPress Enter to continue...")

def import_export_menu(cursor, conn, table_name):
    """Handle import/export operations"""
    import csv
    import json
    
    options = ["Import CSV", "Export CSV", "Export JSON", "Export Markdown", "Back"]
    selected = 0
    
    while True:
        clear_screen()
        console.print(Panel(f"[bold cyan]Import/Export - {table_name}[/bold cyan]", expand=False))
        console.print()
        
        for i, option in enumerate(options):
            if i == selected:
                console.print(f"[black on #E0F7FA]> {option} <[/black on #E0F7FA]")
            else:
                console.print(f"  {option}")
        
        console.print("\n[dim]Use arrow keys to navigate, ENTER to select, ESC to go back[/dim]")
        
        key = readchar.readkey()
        if key == readchar.key.UP:
            selected = (selected - 1) % len(options)
        elif key == readchar.key.DOWN:
            selected = (selected + 1) % len(options)
        elif key == readchar.key.ENTER:
            if selected == 4:  # Back
                break
            elif selected == 0:  # Import CSV
                import_csv(cursor, conn, table_name, csv)
            elif selected == 1:  # Export CSV
                export_csv(cursor, table_name, csv)
            elif selected == 2:  # Export JSON
                export_json(cursor, table_name, json)
            elif selected == 3:  # Export Markdown
                export_markdown(cursor, table_name)
        elif key == readchar.key.ESC:
            break

def import_csv(cursor, conn, table_name, csv):
    """Import data from CSV"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Import CSV - {table_name}[/bold cyan]", expand=False))
    
    filename = console.input("\n[yellow]Enter CSV filename:[/yellow] ").strip()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            # Get table columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            table_cols = [col[1] for col in cursor.fetchall()]
            
            console.print(f"\n[dim]CSV columns: {', '.join(headers)}[/dim]")
            console.print(f"[dim]Table columns: {', '.join(table_cols)}[/dim]")
            
            confirm = console.input("\n[yellow]Proceed with import? (y/n):[/yellow] ").strip().lower()
            
            if confirm == 'y':
                count = 0
                placeholders = ",".join(["?" for _ in headers])
                for row in reader:
                    cursor.execute(f"INSERT INTO {table_name} ({','.join(headers)}) VALUES ({placeholders})", row)
                    count += 1
                
                conn.commit()
                console.print(f"\n[bold green]✓ Imported {count} rows successfully![/bold green]")
            else:
                console.print("[yellow]Import cancelled.[/yellow]")
    
    except FileNotFoundError:
        console.print(f"[red]File '{filename}' not found![/red]")
    except Exception as e:
        console.print(f"[red]Error importing CSV: {e}[/red]")
    
    input("\nPress Enter to continue...")

def export_csv(cursor, table_name, csv):
    """Export table to CSV"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Export CSV - {table_name}[/bold cyan]", expand=False))
    
    filename = console.input("\n[yellow]Enter output filename (without .csv):[/yellow] ").strip()
    filename = f"{filename}.csv"
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        console.print(f"\n[bold green]✓ Exported {len(rows)} rows to {filename}![/bold green]")
    
    except Exception as e:
        console.print(f"[red]Error exporting CSV: {e}[/red]")
    
    input("\nPress Enter to continue...")

def export_json(cursor, table_name, json):
    """Export table to JSON"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Export JSON - {table_name}[/bold cyan]", expand=False))
    
    filename = console.input("\n[yellow]Enter output filename (without .json):[/yellow] ").strip()
    filename = f"{filename}.json"
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        console.print(f"\n[bold green]✓ Exported {len(rows)} rows to {filename}![/bold green]")
    
    except Exception as e:
        console.print(f"[red]Error exporting JSON: {e}[/red]")
    
    input("\nPress Enter to continue...")

def export_markdown(cursor, table_name):
    """Export table to Markdown using Rich Table"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Export Markdown - {table_name}[/bold cyan]", expand=False))
    
    filename = console.input("\n[yellow]Enter output filename (without .md):[/yellow] ").strip()
    filename = f"{filename}.md"
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Build markdown table
        md_lines = [f"# Table: {table_name}\n"]
        md_lines.append("| " + " | ".join(columns) + " |")
        md_lines.append("| " + " | ".join(["---" for _ in columns]) + " |")
        
        for row in rows:
            md_lines.append("| " + " | ".join([str(cell) for cell in row]) + " |")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(md_lines))
        
        console.print(f"\n[bold green]✓ Exported {len(rows)} rows to {filename}![/bold green]")
    
    except Exception as e:
        console.print(f"[red]Error exporting Markdown: {e}[/red]")
    
    input("\nPress Enter to continue...")

def execute_custom_sql(cursor, conn, table_name):
    """Execute custom SQL query on the table"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Custom SQL Query - {table_name}[/bold cyan]", expand=False))
    
    console.print("\n[dim]Enter your SQL query (use {table} as placeholder for table name):[/dim]")
    console.print("[dim]Example: SELECT * FROM {table} WHERE column > 10[/dim]\n")
    
    query = console.input("[yellow]SQL:[/yellow] ").strip()
    
    if not query:
        console.print("[red]Query cannot be empty![/red]")
        input("\nPress Enter to continue...")
        return
    
    # Replace {table} placeholder
    query = query.replace("{table}", table_name)
    
    try:
        cursor.execute(query)
        
        # Check if it's a SELECT query
        if query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            
            if not rows:
                console.print("\n[yellow]Query returned no results.[/yellow]")
            else:
                # Get column names from cursor description
                columns = [desc[0] for desc in cursor.description]
                
                # Create Rich table
                rich_table = Table(title=f"[bold green]Query Results ({len(rows)} rows)[/bold green]")
                
                for col in columns:
                    rich_table.add_column(f"[bold cyan]{col}[/bold cyan]", style="white")
                
                for row in rows:
                    rich_table.add_row(*[str(cell) for cell in row])
                
                console.print()
                console.print(rich_table)
        else:
            # For non-SELECT queries (INSERT, UPDATE, DELETE)
            conn.commit()
            console.print(f"\n[bold green]✓ Query executed successfully! Rows affected: {cursor.rowcount}[/bold green]")
    
    except sqlite3.Error as e:
        console.print(f"\n[red]SQL Error: {e}[/red]")
    
    input("\nPress Enter to continue...")

def show_table_data(cursor, conn, table_name):
    """Display first 20 rows of the selected table with buttons"""
    buttons = ["Row Editing", "Search/Filter", "Table Info", "Import/Export", "Custom SQL"]
    selected = 0
    
    while True:
        clear_screen()
        term_width, term_height = shutil.get_terminal_size()
        
        # Fetch table data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 20")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Create Rich table
        rich_table = Table(title=f"[bold #CC22BB]Table: {table_name}[/bold #CC22BB]")
        
        # Add columns with color
        for col in columns:
            rich_table.add_column(f"[bold cyan]{col}[/bold cyan]", style="white")
        
        # Add rows
        for row in rows:
            rich_table.add_row(*[str(cell) for cell in row])
        
        # Print table
        console.print(rich_table)
        console.print()
        
        # Print buttons
        button_lines = []
        for i, button in enumerate(buttons):
            if i == selected:
                button_lines.append(f"[black on #E0F7FA]> {button} <[/black on #E0F7FA]")
            else:
                button_lines.append(f"  {button}  ")
        
        console.print("  ".join(button_lines))
        console.print("\n[dim]Use arrow keys to navigate, ENTER to select, ESC to go back[/dim]")
        
        key = readchar.readkey()
        if key == readchar.key.LEFT:
            selected = (selected - 1) % len(buttons)
        elif key == readchar.key.RIGHT:
            selected = (selected + 1) % len(buttons)
        elif key == readchar.key.ENTER:
            if selected == 0:  # Row Editing
                row_editing_menu(cursor, conn, table_name)
            elif selected == 1:  # Search/Filter
                search_filter(cursor, table_name)
            elif selected == 2:  # Table Info
                table_info(cursor, table_name)
            elif selected == 3:  # Import/Export
                import_export_menu(cursor, conn, table_name)
            elif selected == 4:  # Custom SQL
                execute_custom_sql(cursor, conn, table_name)
        elif key == readchar.key.ESC or key in [readchar.key.CTRL_C]:
            break

def main_loop(database_name):
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
        # ASCII art
        ascii_art = """               
 ____  ____  ____  _  _ 
(_  _)(  _ \(  _ \( \/ )
  )(   )(_) )) _ < \  / 
 (__) (____/(____/  \/  
 """

        while True:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]

            # Menu options: "CREATE NEW TABLE" + existing tables
            options = ["CREATE NEW TABLE"] + tables
            selected = 0

            while True:
                clear_screen()
                term_width, term_height = shutil.get_terminal_size()

                # Build menu text
                menu_lines = [
                    f"[#ed2e1c]{ascii_art}[/#ed2e1c]\n",
                    f"Connected to [#CC22BB on black]{database_name}.db[/#CC22BB on black]\n"
                ]
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
                    if selected == 0:
                        # CREATE NEW TABLE selected
                        create_new_table(cursor, conn)
                        break  # Refresh the menu to show new table
                    else:
                        # A table was selected
                        table_name = options[selected]
                        show_table_data(cursor, conn, table_name)
                elif key in [readchar.key.CTRL_C, readchar.key.CTRL_X, readchar.key.CTRL_Z]:
                    clear_screen()
                    console.print("Exiting...")
                    conn.close()
                    return

if __name__ == "__main__":
    db_name = input("Enter database name (without .db): ")
    main_loop(db_name)
