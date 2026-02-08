import loader
import dashboard

DATA_FILE = "gdp.csv"

data = loader.load_data(DATA_FILE)
regions = dashboard.get_all_regions(data)
year = dashboard.get_latest_year(data)

print("Launching interactive dashboard...")
dashboard.create_dashboard(data, regions, year)
