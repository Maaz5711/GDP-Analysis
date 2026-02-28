import csv
import json
import os


class CSVReader:
    """
    Reads GDP data from a CSV file and sends it to the pipeline.
    Same logic as src/loader.py — reads wide CSV, converts to long format.
    """

    def __init__(self, service, filepath):
        self.service = service  # the engine (PipelineService)
        self.filepath = filepath

    def run(self):
        """Read the CSV, clean it, and pass to the engine."""
        raw_data = self._load_csv()
        cleaned = self._clean_data(raw_data)
        self.service.execute(cleaned)

    def _load_csv(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError("File not found: " + self.filepath)

        raw_data = []
        with open(self.filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_data.append(row)
        return raw_data

    def _clean_data(self, data):
        """Convert wide format (one column per year) to long format."""
        if not data:
            return []

        # find all columns that are years
        years = [key for key in data[0].keys() if key.isdigit()]
        cleaned = []

        for row in data:
            for year in years:
                value = row.get(year)

                # skip empty values
                if value and value.strip() != "":
                    value = value.replace(",", "")
                    cleaned.append({
                        "Country": row["Country Name"],
                        "Region": row["Continent"],
                        "Year": int(year),
                        "Value": float(value),
                    })

        return cleaned


class JSONReader:
    """
    Reads GDP data from a JSON file and sends it to the pipeline.
    Expects data already in long format:
    [{"Country": "...", "Region": "...", "Year": 2020, "Value": 123.45}, ...]
    """

    def __init__(self, service, filepath):
        self.service = service  # the engine (PipelineService)
        self.filepath = filepath

    def run(self):
        """Read the JSON and pass to the engine."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError("File not found: " + self.filepath)

        with open(self.filepath, mode="r", encoding="utf-8") as f:
            data = json.load(f)

        self.service.execute(data)
