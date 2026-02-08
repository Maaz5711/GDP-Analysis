import csv
import os

def load_data(filepath):

    if not os.path.exists(filepath):
        raise FileNotFoundError("File not found.")

    raw_data = []

    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_data.append(row)

    except Exception:
        raise IOError("Error reading CSV file.")

    return clean_data(raw_data)


def clean_data(data):

    if not data:
        return []

    years = [key for key in data[0].keys() if key.isdigit()]

    cleaned = []

    for row in data:
        for year in years:
            value = row.get(year)

            if value and value.strip() != "":
                value = value.replace(",", "")

                cleaned.append({
                    "Country": row["Country Name"],
                    "Region": row["Continent"],
                    "Year": int(year),
                    "Value": float(value)
                })

    return cleaned

