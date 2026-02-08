import csv
import os

def load_data(filepath):
    # file exists?
    if not os.path.exists(filepath):
        raise FileNotFoundError("File not found.")

    raw_data = []

    # open file and read as rows
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_data.append(row)

    return clean_data(raw_data)


def clean_data(data):
    if not data:
        return []

    # find all columns with years
    years = [key for key in data[0].keys() if key.isdigit()]

    cleaned = []

    # loop through each country row
    for row in data:
        for year in years:
            value = row.get(year)

            # skip empty values
            if value and value.strip() != "":
                # removing commas
                value = value.replace(",", "")
                
                cleaned.append({
                    "Country": row["Country Name"],
                    "Region": row["Continent"],
                    "Year": int(year),
                    "Value": float(value)
                })

    return cleaned
