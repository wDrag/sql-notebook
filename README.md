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
