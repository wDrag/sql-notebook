# SQL Notebook with Virtual Environment

A structured SQL notebook project with a virtual environment setup for managing SQL queries, schemas, and data analysis.

## Project Structure

```
notebooks/
├── exploratory/      # Exploratory SQL queries and analysis
├── analysis/         # Production-ready analysis queries
├── migrations/       # Database migration scripts
├── optimization/     # Query optimization experiments
└── documentation/    # SQL documentation and guides
scripts/
├── setup/           # Setup and initialization scripts
│   ├── init.sh      # Initialize virtual environment
│   ├── install.sh   # Install dependencies
│   ├── dev.sh       # Run in development mode
│   └── prod.sh      # Run in production mode
├── etl/             # ETL (Extract, Transform, Load) scripts
└── utilities/       # Utility scripts
data/
├── sample/          # Sample data files
└── exports/         # Exported data files
schema/
├── ddl/             # Data Definition Language (CREATE, ALTER, DROP)
├── dml/             # Data Manipulation Language (INSERT, UPDATE, DELETE)
└── constraints/     # Database constraints and indexes
```

## SQL Magic Commands

This project uses [ipython-sql](https://github.com/catherinedevlin/ipython-sql) to enable SQL magic commands in Jupyter notebooks. SQL magic provides a convenient way to run SQL queries directly in notebook cells.

### Installation

SQL magic is already included in the project dependencies. It will be installed when you run:

```bash
make install
```

### Loading SQL Magic

To use SQL magic in a Jupyter notebook, load the extension at the beginning of your notebook:

```python
%load_ext sql
```

### Connecting to a Database

Connect to your database using a connection string:

```python
# PostgreSQL
%sql postgresql://username:password@localhost:5432/database_name

# MySQL
%sql mysql://username:password@localhost:3306/database_name

# SQLite
%sql sqlite:///path/to/database.db
```

For better security, use environment variables for credentials:

```python
import os
%sql postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/mydb
```

### Using SQL Magic

#### Line Magic (`%sql`)

Execute a single-line SQL query:

```python
%sql SELECT * FROM users LIMIT 10
```

#### Cell Magic (`%%sql`)

Execute multi-line SQL queries:

```python
%%sql
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name
ORDER BY order_count DESC
LIMIT 10
```

#### Storing Results

Save query results to a Python variable:

```python
result = %sql SELECT * FROM users WHERE status = 'active'

# Convert to pandas DataFrame
df = result.DataFrame()
```

#### Parameterized Queries

Use Python variables in SQL queries:

```python
user_id = 123
%sql SELECT * FROM users WHERE id = :user_id
```

### Common SQL Magic Options

- `%sql --persist` - Save query results to a temporary table
- `%sql --append` - Append results to an existing table
- `%%sql result <<` - Store results in a variable named 'result'
- `%config SqlMagic.autopandas = True` - Automatically return results as pandas DataFrames
- `%config SqlMagic.feedback = False` - Disable feedback messages

### Example Workflow

```python
# Load the extension
%load_ext sql

# Connect to database
%sql postgresql://localhost/mydb

# Configure autopandas
%config SqlMagic.autopandas = True

# Run a query and get results as DataFrame
df = %sql SELECT * FROM sales WHERE date > '2024-01-01'

# Use the DataFrame with pandas
print(df.describe())
```

## Usage

Use `make <script_name>` to execute the corresponding script.

### Initialize Project

```bash
make init
```

### Install Dependencies

```bash
make install
```

### Run in Development Environment

```bash
make dev
```

### Run in Production Environment

```bash
make prod
```

### Generate PDF Reports

To generate PDF reports from notebooks, use the following command:

```bash
make pdf <notebook_path> <output_path>
```

Replace `<notebook_path>` with the path to the notebook you want to convert and `<output_path>` with the desired output file path.
