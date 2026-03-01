import csv
import json
import os


class CSVReader:
    # Reads GDP data from a CSV file and sends it to the engine.

    def __init__(self, service, filepath):
        self.service = service
        self.filepath = filepath

    def run(self):
        raw_rows = self.read_csv()
        long_format = self.convert_to_long_format(raw_rows)
        self.service.execute(long_format)

    def read_csv(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError("File not found: " + self.filepath)

        rows = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows

    def convert_to_long_format(self, rows):
        # The CSV has one column per year (wide format).
        # We convert it so each row is one country + one year (long format).
        
        if not rows:
            return []

        # find which columns are years
        year_columns = [col for col in rows[0].keys() if col.isdigit()]
        result = []

        for row in rows:
            for year in year_columns:
                value = row.get(year, "")

                # skip empty cells
                if value and value.strip() != "":
                    result.append({
                        "Country": row["Country Name"],
                        "Region": row["Continent"],
                        "Year": int(year),
                        "Value": float(value.replace(",", "")),
                    })

        return result


class JSONReader:
    # Reads GDP data from a JSON file and sends it to the engine.

    def __init__(self, service, filepath):
        self.service = service
        self.filepath = filepath

    def run(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError("File not found: " + self.filepath)

        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.service.execute(data)
