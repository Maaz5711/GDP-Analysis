# GDP Analysis Dashboard

A beginner-friendly project that explores World Bank GDP data and turns it into clear, visual insights. It is built as a small, modular Python app so each part has a focused job.

## What this project does
- 📥 Loads GDP data from a CSV file.
- 🌍 Lets you explore global and regional GDP trends.
- 🏆 Highlights the top/latest economies for a selected year.
- 📊 Creates charts you can view live or save as images.

## What the dashboard shows
- 🖱️ A simple side panel lets you switch between international and regional views.
- 🥧 The international view shows a pie chart of regional GDP shares and a bar chart of the top 10 economies.
- 📈 The regional view shows a GDP growth bar chart for the leading country and a trend line for the region.

## How it works (short and simple)
- **`main.py`** starts the app, loads the data, and opens the dashboard.
- **`loader.py`** reads and cleans the CSV file.
- **`processor.py`** provides filtering and basic calculations.
- **`dashboard.py`** draws the charts and handles the region selector.
- **`generate_images.py`** saves the charts to files for reports.
- **`generate_report.py`** is a starter script you can expand for custom reports.
- **`config.json`** is a placeholder settings file if you want to add configuration-driven runs later (for example: region, year, or operation choices).

## Data
The sample dataset lives in `data/gdp.csv` and is loaded automatically when you run the app.

GitHub Actions runs the image generator on code pushes and pull requests. The charts are uploaded as downloadable artifacts in the Actions tab.
