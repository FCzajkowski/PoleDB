# TDBV
> [!IMPORTANT]
> Project is still in early development, there might be some issues. If any accure, please **create new issue**

> [!NOTE]
> To run project you will need python (>3.7)
### What's Inside

A beautiful, terminal-based SQLite database management tool with an intuitive interface built using Rich library.

## Features

- 🎨 **Beautiful TUI** - Rich terminal interface with colors and formatted tables
- 📊 **Table Management** - Create, view, and manage SQLite tables
- ✏️ **Row Operations** - Insert, edit, delete, and truncate rows
- 🔍 **Search & Filter** - Advanced search with custom SQL conditions
- 📤 **Import/Export** - Support for CSV, JSON, and Markdown formats
- 🔧 **Custom SQL** - Execute custom queries with formatted results
- ℹ️ **Table Info** - View detailed column information, indexes, and statistics

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
pip install rich readchar
```

Or using a requirements file:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
rich>=13.0.0
readchar>=4.0.0
```

## Usage

### Basic Usage

```bash
python main.py <database_name>
```

**Example:**
```bash
python main.py myapp
```

This will create/open `myapp.db` in the current directory.

### Navigation

- **Arrow Keys** - Navigate menu options and buttons
- **Enter** - Select an option
- **ESC** - Go back to previous menu
- **Ctrl+C/X/Z** - Exit application

## Main Menu

When you launch IDBBY, you'll see:

```
 ____  ____  ____  _  _ 
(_  _)(  _ \(  _ \( \/ )
  )(   )(_) )) _ < \  / 
 (__) (____/(____/  \/  

Connected to myapp.db

> CREATE NEW TABLE <
existing_table_1
existing_table_2
```

### Create New Table

Select **CREATE NEW TABLE** to launch the interactive table creator:

1. **Enter table name**
2. **Add columns** with the following options:
   - Column name
   - Data type (INTEGER, TEXT, REAL, BLOB, NUMERIC)
   - Primary Key
   - NOT NULL constraint
   - UNIQUE constraint
   - Default value
3. **Review SQL** before creation
4. **Confirm** to create the table

**Example:**
```
Table: users

Columns:
1. id - INTEGER (PRIMARY KEY)
2. username - TEXT (NOT NULL, UNIQUE)
3. email - TEXT (NOT NULL)
4. created_at - TEXT (DEFAULT: 'CURRENT_TIMESTAMP')
```

## Table View Features

When you select a table, you'll see the first 20 rows and five action buttons:

### 1. Row Editing

**Insert Row:**
- Fill in values for each column
- Auto-increment primary keys are skipped
- Default values are automatically applied
- Required fields (NOT NULL) are enforced

**Edit Row:**
- Select a row by primary key
- View current values
- Enter new values (press Enter to keep current)
- Only modified fields are updated

**Delete Row:**
- Select a row by primary key
- Confirmation required
- Safe deletion using primary key

**Truncate:**
- Delete all rows from the table
- Type "DELETE ALL" to confirm
- Shows row count before deletion

### 2. Search/Filter

Execute custom WHERE conditions:

```
Column: age
Query: > 18

Column: username
Query: LIKE '%john%'

Column: status
Query: = 'active'
```

Results are displayed in a formatted table.

### 3. Table Info

View comprehensive table information:

- **Column details** (name, type, constraints)
- **Row count**
- **Index information**
- **Primary keys** and **unique constraints**

### 4. Import/Export

**Import CSV:**
- Provide CSV filename
- Column mapping is automatic
- Headers must match table columns
- Bulk insert with transaction

**Export CSV:**
- Exports all rows to CSV
- Includes column headers
- UTF-8 encoding

**Export JSON:**
- Exports as array of objects
- Pretty-printed with indentation
- UTF-8 encoding with Unicode support

**Export Markdown:**
- Creates Markdown table format
- Suitable for documentation
- Includes table title

### 5. Custom SQL

Execute any SQL query with `{table}` as placeholder:

```sql
SELECT * FROM {table} WHERE created_at > '2024-01-01'

UPDATE {table} SET status = 'active' WHERE id < 100

DELETE FROM {table} WHERE expires_at < date('now')
```

- **SELECT queries** show formatted results
- **Modification queries** (INSERT, UPDATE, DELETE) show affected row count
- Error messages for invalid SQL

## Project Structure

```
project/
├── main.py              # Entry point with CLI argument handling
├── scripts/
│   └── runtime.py       # Core application logic
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Error Codes

- **1001** - No Database Selected (missing argument)
- **1002** - More Than One Argument Passed

## SQLite Data Types

IDBBY supports all SQLite data types:

- **INTEGER** - Signed integers
- **TEXT** - UTF-8 text strings
- **REAL** - Floating-point numbers
- **BLOB** - Binary data (stored as-is)
- **NUMERIC** - Numeric values (flexible storage)

## Tips & Best Practices

1. **Primary Keys**: Always define a primary key for safe row editing and deletion
2. **Backups**: Make regular backups of your `.db` files before bulk operations
3. **Transactions**: Import/export operations use transactions for data integrity
4. **Large Tables**: Only first 20 rows are displayed for performance
5. **Custom SQL**: Use the custom SQL feature for complex queries beyond the UI

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ↑/↓ | Navigate vertically (menus) |
| ←/→ | Navigate horizontally (buttons) |
| Enter | Select/Confirm |
| ESC | Back/Cancel |
| Ctrl+C | Exit application |

## Troubleshooting

**Issue: "Database did NOT load"**
- Check file permissions
- Ensure SQLite3 is installed
- Verify database file is not corrupted

**Issue: Import fails**
- Verify CSV column names match table columns
- Check for data type mismatches
- Ensure CSV is UTF-8 encoded

**Issue: Can't edit/delete rows**
- Table must have a primary key defined
- Use custom SQL as alternative

## Technical Details

- **Library**: Rich (for terminal UI)
- **Database**: SQLite3 (built-in)
- **Input**: readchar (for keyboard handling)
- **Platform**: Cross-platform (Windows, macOS, Linux)

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Contributions are welcome! Areas for improvement:

- Pagination for large tables
- Foreign key relationship visualization
- Query history
- Syntax highlighting for SQL
- Database schema export
- Multi-table joins interface

## Author

Built with ❤️ for easy SQLite database management.

## Version

Current Version: 1.0.0

---

**Happy Database Managing! 🎉**
