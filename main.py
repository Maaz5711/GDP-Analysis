from src import loader
from src import dashboard

DATA_FILE = "data/gdp.csv" #name of the data file

data = loader.load_data(DATA_FILE)
regions = dashboard.get_all_regions(data)
year = dashboard.get_latest_year(data)

print("------Loading dashboard------") #show output in a seperate window
dashboard.create_dashboard(data, regions, year)
