# GDP Analysis Dashboard

This repository contains a Python-based GDP analysis dashboard built around World Bank GDP data. It includes an interactive Matplotlib dashboard along with a headless script that generates static PNG reports for the GitHub Actions workflow.

## Repository layout

- `main.py` - entry point for the interactive dashboard (uses a hardcoded `DATA_FILE = "gdp.csv"` path to a GDP CSV and requires `PYTHONPATH` setup).
- `src/loader.py` - CSV loading and data cleaning logic.
- `src/processor.py` - filters and summary calculations.
- `src/dashboard.py` - plotting logic and interactive dashboard UI.
- `src/generate_images.py` - saves dashboard charts to `output_charts/` (used in CI).
- `src/generate_report.py` - scaffold for additional reporting.
- `data/gdp.csv` - GDP dataset used by the scripts.
- `config.json` - reserved for configuration-driven options (currently unused; default empty object).

## Requirements

- Python 3.10+
- Install dependencies: `pip install -r src/requirements.txt`

## Data format

`data/gdp.csv` expects the columns `Country Name`, `Continent`, and year columns (e.g. `1990`, `1991`, ...). The loader expands each year column into `Country`, `Region`, `Year`, and `Value` rows.

## Usage

### Interactive dashboard

`main.py` references `DATA_FILE = "gdp.csv"` by default (a file in the repo root). To run the dashboard with the provided dataset, either copy `data/gdp.csv` to `gdp.csv` in the root or update `DATA_FILE` to `data/gdp.csv`, then run:

```bash
PYTHONPATH=src python main.py
```

This launches a Matplotlib window with region selectors and two charts.

### Generate PNG reports

To generate static images (the same step used in CI):

```bash
python src/generate_images.py
```

Images are written to `output_charts/`.

## GitHub Actions

On pushes and pull requests targeting `main`, the workflow runs `src/generate_images.py` and uploads the PNG artifacts.
