# These are aggregate/group names in the CSV, not actual countries.
# We skip these when doing country-level analysis.
NON_COUNTRY_NAMES = {
    "World", "Africa Eastern and Southern", "Africa Western and Central",
    "Arab World", "Caribbean small states",
    "Central Europe and the Baltics", "Early-demographic dividend",
    "East Asia & Pacific", "East Asia & Pacific (IDA & IBRD countries)",
    "East Asia & Pacific (excluding high income)", "Euro area",
    "Europe & Central Asia", "Europe & Central Asia (IDA & IBRD countries)",
    "Europe & Central Asia (excluding high income)", "European Union",
    "High income", "IBRD only", "IDA & IBRD total", "IDA blend",
    "IDA only", "IDA total", "Late-demographic dividend",
    "Latin America & Caribbean",
    "Latin America & Caribbean (excluding high income)",
    "Latin America & the Caribbean (IDA & IBRD countries)",
    "Low & middle income", "Low income", "Lower middle income",
    "Middle East, North Africa, Afghanistan & Pakistan",
    "Middle East, North Africa, Afghanistan & Pakistan (IDA & IBRD)",
    "Middle East, North Africa, Afghanistan & Pakistan (excluding high income)",
    "Middle income", "North America", "OECD members",
    "Other small states", "Pacific island small states",
    "Post-demographic dividend", "Pre-demographic dividend",
    "Small states", "South Asia", "South Asia (IDA & IBRD)",
    "Sub-Saharan Africa", "Sub-Saharan Africa (IDA & IBRD countries)",
    "Sub-Saharan Africa (excluding high income)", "Upper middle income",
    "West Bank and Gaza", "Fragile and conflict affected situations",
    "Heavily indebted poor countries (HIPC)",
    "Least developed countries: UN classification",
    "Not classified",
}

VALID_REGIONS = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]


class TransformationEngine:
    # Takes raw GDP data and runs analyses on it.
    # Results are sent to a 'sink' (console or chart output).
    

    def __init__(self, sink, config):
        self.sink = sink
        self.config = config

    # Main entry point (called by the input reader)

    def execute(self, raw_data):
        for analysis in self.config.get("analyses", []):
            name = analysis["name"]

            if name == "top_10":
                self.top_10(raw_data, analysis)
            elif name == "bottom_10":
                self.bottom_10(raw_data, analysis)
            elif name == "growth_rate":
                self.growth_rate(raw_data, analysis)
            elif name == "avg_gdp_by_continent":
                self.avg_gdp_by_continent(raw_data, analysis)
            elif name == "global_gdp_trend":
                self.global_gdp_trend(raw_data, analysis)
            elif name == "fastest_growing_continent":
                self.fastest_growing_continent(raw_data, analysis)
            elif name == "consistent_decline":
                self.consistent_decline(raw_data, analysis)
            elif name == "continent_contribution":
                self.continent_contribution(raw_data, analysis)
            else:
                print("Unknown analysis:", name)

    # Helper functions

    def only_countries(self, data):
        # Remove aggregate entries, keep only real countries.
        return [row for row in data if row["Country"] not in NON_COUNTRY_NAMES]

    def by_region(self, data, region):
        return [row for row in data if row["Region"] == region]

    def by_year(self, data, year):
        return [row for row in data if row["Year"] == year]

    def by_year_range(self, data, start, end):
        return [row for row in data if start <= row["Year"] <= end]

    def gdp_values(self, data):
        return [row["Value"] for row in data]

    def total(self, values):
        return sum(values) if values else 0.0

    def average(self, values):
        return sum(values) / len(values) if values else 0.0

    def get_regions(self, data):
        found = set(row["Region"] for row in data)
        return sorted(r for r in found if r in VALID_REGIONS)

    def get_countries(self, data):
        return sorted(set(row["Country"] for row in data))

    def latest_year(self, data):
        return max(row["Year"] for row in data)

    # Analysis functions

    def top_10(self, data, analysis):
        continent = analysis["continent"]
        year = analysis["year"]

        filtered = self.by_year(self.by_region(data, continent), year)
        filtered = self.only_countries(filtered)
        filtered = sorted(filtered, key=lambda x: x["Value"], reverse=True)

        results = []
        for row in filtered[:10]:
            results.append({"Country": row["Country"], "GDP": row["Value"]})

        title = "Top 10 Countries by GDP — " + continent + " (" + str(year) + ")"
        self.sink.write(title, results)

    def bottom_10(self, data, analysis):
        continent = analysis["continent"]
        year = analysis["year"]

        filtered = self.by_year(self.by_region(data, continent), year)
        filtered = self.only_countries(filtered)
        filtered = sorted(filtered, key=lambda x: x["Value"])

        results = []
        for row in filtered[:10]:
            results.append({"Country": row["Country"], "GDP": row["Value"]})

        title = "Bottom 10 Countries by GDP — " + continent + " (" + str(year) + ")"
        self.sink.write(title, results)

    def growth_rate(self, data, analysis):
        continent = analysis["continent"]
        start_year = analysis["start_year"]
        end_year = analysis["end_year"]

        filtered = self.only_countries(self.by_region(data, continent))
        countries = self.get_countries(filtered)
        results = []

        for country in countries:
            country_rows = [r for r in filtered if r["Country"] == country]
            start_rows = [r for r in country_rows if r["Year"] == start_year]
            end_rows = [r for r in country_rows if r["Year"] == end_year]

            if start_rows and end_rows and start_rows[0]["Value"] > 0:
                start_val = start_rows[0]["Value"]
                end_val = end_rows[0]["Value"]
                growth = ((end_val - start_val) / start_val) * 100
                results.append({"Country": country, "Growth Rate (%)": round(growth, 2)})

        results = sorted(results, key=lambda x: x["Growth Rate (%)"], reverse=True)
        title = "GDP Growth Rate — " + continent + " (" + str(start_year) + "-" + str(end_year) + ")"
        self.sink.write(title, results)

    def avg_gdp_by_continent(self, data, analysis):
        start_year = analysis["start_year"]
        end_year = analysis["end_year"]

        filtered = self.only_countries(self.by_year_range(data, start_year, end_year))
        results = []

        for region in self.get_regions(filtered):
            region_data = self.by_region(filtered, region)
            avg = self.average(self.gdp_values(region_data))
            results.append({"Continent": region, "Average GDP": round(avg, 2)})

        results = sorted(results, key=lambda x: x["Average GDP"], reverse=True)
        title = "Average GDP by Continent (" + str(start_year) + "-" + str(end_year) + ")"
        self.sink.write(title, results)

    def global_gdp_trend(self, data, analysis):
        start_year = analysis["start_year"]
        end_year = analysis["end_year"]

        filtered = self.only_countries(self.by_year_range(data, start_year, end_year))
        years = sorted(set(row["Year"] for row in filtered))
        results = []

        for year in years:
            year_total = self.total(self.gdp_values(self.by_year(filtered, year)))
            results.append({"Year": year, "Total Global GDP": round(year_total, 2)})

        title = "Total Global GDP Trend (" + str(start_year) + "-" + str(end_year) + ")"
        self.sink.write(title, results)

    def fastest_growing_continent(self, data, analysis):
        start_year = analysis["start_year"]
        end_year = analysis["end_year"]

        filtered = self.only_countries(data)
        results = []

        for region in self.get_regions(filtered):
            region_data = self.by_region(filtered, region)
            start_total = self.total(self.gdp_values(self.by_year(region_data, start_year)))
            end_total = self.total(self.gdp_values(self.by_year(region_data, end_year)))

            if start_total > 0:
                growth = ((end_total - start_total) / start_total) * 100
                results.append({"Continent": region, "Growth Rate (%)": round(growth, 2)})

        results = sorted(results, key=lambda x: x["Growth Rate (%)"], reverse=True)
        title = "Fastest Growing Continent (" + str(start_year) + "-" + str(end_year) + ")"
        self.sink.write(title, results)

    def consistent_decline(self, data, analysis):
        last_x_years = analysis["last_x_years"]
        latest = self.latest_year(data)
        start_year = latest - last_x_years + 1

        filtered = self.only_countries(self.by_year_range(data, start_year, latest))
        countries = self.get_countries(filtered)
        results = []

        for country in countries:
            rows = sorted(
                [r for r in filtered if r["Country"] == country],
                key=lambda x: x["Year"]
            )

            if len(rows) < 2:
                continue

            # check if GDP went down every single year
            declining = True
            for i in range(1, len(rows)):
                if rows[i]["Value"] >= rows[i - 1]["Value"]:
                    declining = False
                    break

            if declining:
                results.append({
                    "Country": country,
                    "GDP (" + str(start_year) + ")": rows[0]["Value"],
                    "GDP (" + str(latest) + ")": rows[-1]["Value"],
                })

        title = "Countries with Consistent GDP Decline (Last " + str(last_x_years) + " Years)"
        self.sink.write(title, results)

    def continent_contribution(self, data, analysis):
        start_year = analysis["start_year"]
        end_year = analysis["end_year"]

        filtered = self.only_countries(self.by_year_range(data, start_year, end_year))
        total_gdp = self.total(self.gdp_values(filtered))
        results = []

        for region in self.get_regions(filtered):
            region_total = self.total(self.gdp_values(self.by_region(filtered, region)))
            percentage = (region_total / total_gdp) * 100 if total_gdp > 0 else 0
            results.append({"Continent": region, "Contribution (%)": round(percentage, 2)})

        results = sorted(results, key=lambda x: x["Contribution (%)"], reverse=True)
        title = "Contribution of Each Continent to Global GDP (" + str(start_year) + "-" + str(end_year) + ")"
        self.sink.write(title, results)
