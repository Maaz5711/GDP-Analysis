# src/generate_report.py
import matplotlib.pyplot as plt
import loader
import processor
import os

# Create output folder
if not os.path.exists('output'):
    os.makedirs('output')

DATA_FILE = 'data/gdp.csv' # Note: Adjust path based on where you run it
data = loader.load_data(DATA_FILE)

# 1. Generate International Plots
year = 2020 # Or use your get_latest_year logic

# Re-using your logic manually for static output
# ... (Copy your plotting logic here but replace plt.show() with plt.savefig()) ...

print("Generating International Pie Chart...")
plt.figure()
# ... [Insert your plot_international_pie logic here] ...
plt.savefig('output/international_pie.png')
plt.close()

print("Generating International Bar Chart...")
plt.figure()
# ... [Insert your plot_international_bar logic here] ...
plt.savefig('output/international_bar.png')
plt.close()

# 2. Generate Regional Plots Loop
regions = ['Asia', 'Europe', 'Africa'] # Add all your regions
for region in regions:
    print(f"Generating charts for {region}...")
    
    plt.figure()
    # ... [Insert your plot_regional_line logic here] ...
    plt.title(f"{region} GDP Trend")
    plt.savefig(f'output/{region}_trend.png')
    plt.close()

print("All charts saved to /output folder.")
