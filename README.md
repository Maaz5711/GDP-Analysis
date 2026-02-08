# GDP Analysis Dashboard

A beginner-friendly project that explores World Bank GDP data and turns it into clear, visual insights. It is built as a small, modular Python app so each part has a focused job.

## What this project does
- Loads GDP data from a CSV file.
- Lets you explore global and regional GDP trends.
- Highlights the top economies for a selected year.
- Creates simple charts you can view live or save as images.

## How it works (short and simple)
- **`main.py`** starts the app, loads the data, and opens the dashboard.
- **`loader.py`** reads and cleans the CSV file.
- **`processor.py`** provides filtering and basic calculations.
- **`dashboard.py`** draws the charts and handles the region selector.
- **`generate_images.py`** saves the charts to files for reports.
- **`generate_report.py`** is a starter script you can expand for custom reports.
- **`config.json`** is a small settings file you can fill in if you want to extend the app later.

## Quick start
1. Install dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```
2. Run the dashboard:
   ```bash
   python main.py
   ```
3. (Optional) Save chart images:
   ```bash
   python src/generate_images.py
   ```

## Data
The sample dataset lives in `data/gdp.csv` and is loaded automatically when you run the app.

GitHub Actions is set up to generate dashboard images as workflow artifacts.
