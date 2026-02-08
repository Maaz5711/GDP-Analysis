import sys
import os
import matplotlib.pyplot as tools

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

import loader
import processor

valid_regions = [
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "South America",
    "Oceania",
]

NON_COUNTRY_NAMES = {
    "World",
    "Africa Eastern and Southern",
    "Africa Western and Central",
    "Arab World",
    "Caribbean small states",
    "Central Europe and the Baltics",
    "Early-demographic dividend",
    "East Asia & Pacific",
    "East Asia & Pacific (IDA & IBRD countries)",
    "East Asia & Pacific (excluding high income)",
    "Euro area",
    "Europe & Central Asia",
    "Europe & Central Asia (IDA & IBRD countries)",
    "Europe & Central Asia (excluding high income)",
    "European Union",
    "High income",
    "IBRD only",
    "IDA & IBRD total",
    "IDA blend",
    "IDA only",
    "IDA total",
    "Late-demographic dividend",
    "Latin America & Caribbean",
    "Latin America & Caribbean (excluding high income)",
    "Latin America & the Caribbean (IDA & IBRD countries)",
    "Low & middle income",
    "Low income",
    "Lower middle income",
    "Middle East, North Africa, Afghanistan & Pakistan",
    "Middle East, North Africa, Afghanistan & Pakistan (IDA & IBRD)",
    "Middle East, North Africa, Afghanistan & Pakistan (excluding high income)",
    "Middle income",
    "North America",
    "OECD members",
    "Other small states",
    "Pacific island small states",
    "Post-demographic dividend",
    "Pre-demographic dividend",
    "Small states",
    "South Asia",
    "South Asia (IDA & IBRD)",
    "Sub-Saharan Africa",
    "Sub-Saharan Africa (IDA & IBRD countries)",
    "Sub-Saharan Africa (excluding high income)",
    "Upper middle income",
    "West Bank and Gaza",
}

def plot_regional_histogram(ax, data, region, year):
    region_data = processor.filter_by_region(data, region)

    if region == "Asia":
        top_country = "Pakistan"
    else:
        year_data = processor.filter_by_year(region_data, year)
        year_data = list(
            filter(lambda row: row["Country"] not in NON_COUNTRY_NAMES, year_data)
        )

        if len(year_data) == 0:
            return

        top_country_row = max(year_data, key=lambda x: x["Value"])
        top_country = top_country_row["Country"]

    country_data = list(filter(lambda row: row["Country"] == top_country, region_data))
    country_data = sorted(country_data, key=lambda x: x["Year"])

    years = list(map(lambda row: row["Year"], country_data))
    values = list(map(lambda row: row["Value"] / 1e9, country_data))

    ax.bar(years, values, color="#4CAF50", alpha=0.7, edgecolor="black", width=0.8)
    ax.set_title("GDP Growth - " + top_country)
    ax.set_xlabel("Year")
    ax.set_ylabel("GDP (Billion $)")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)


def plot_regional_line(ax, data, region):
    region_data = processor.filter_by_region(data, region)
    years_set = sorted(list(set(map(lambda row: row["Year"], region_data))))

    calc_year_total = (
        lambda y: processor.calculate_sum(
            processor.get_values(processor.filter_by_year(region_data, y))
        )
        / 1000000000000
    )

    gdp_per_year = list(map(calc_year_total, years_set))

    ax.plot(years_set, gdp_per_year, marker=".", linewidth=2, color="#4CAF50")
    ax.set_title("GDP Trend - " + region)
    ax.set_xlabel("Year")
    ax.set_ylabel("GDP (Trillion $)")
    ax.grid(True, axis="both", linestyle="--", alpha=0.5)


def plot_international_pie(ax, data, year):
    year_data = processor.filter_by_year(data, year)

    def get_region_total(r):
        r_data = processor.filter_by_region(year_data, r)
        vals = processor.get_values(r_data)
        return processor.calculate_sum(vals)

    region_totals = map(lambda r: (r, get_region_total(r)), valid_regions)
    valid_data = list(filter(lambda x: x[1] > 0, region_totals))

    if not valid_data:
        return

    region_names = list(map(lambda x: x[0], valid_data))
    region_values = list(map(lambda x: x[1], valid_data))

    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F"]

    wedges = ax.pie(
        region_values,
        colors=colors,
        startangle=140,
        autopct="%1.1f%%",
        textprops={"fontsize": 6},
    )[0]
    ax.set_title("Regional GDP Distribution (" + str(year) + ")")
    ax.legend(
        wedges,
        region_names,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=3,
        fontsize=7,
        handlelength=1,
        handleheight=1,
    )


def plot_international_bar(ax, data, year):
    year_data = processor.filter_by_year(data, year)
    year_data = list(
        filter(lambda row: row["Country"] not in NON_COUNTRY_NAMES, year_data)
    )

    if len(year_data) == 0:
        return

    sorted_data = sorted(year_data, key=lambda x: x["Value"], reverse=True)
    top_10 = sorted_data[:10]

    countries = list(map(lambda item: item["Country"], top_10))
    values = list(map(lambda item: item["Value"] / 1e12, top_10))

    positions = list(range(len(countries)))

    ax.bar(positions, values, color="#2196F3", alpha=0.8, edgecolor="black", width=0.7)
    ax.set_title("Top 10 Global Economies (" + str(year) + ")")
    ax.set_xlabel("Country")
    ax.set_ylabel("GDP (Trillion $)")
    ax.set_xticks(positions)
    ax.set_xticklabels(countries, rotation=45, ha="right", fontsize=8)
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    DATA_PATH = os.path.join(base_dir, "data", "gdp.csv")
    OUTPUT_DIR = os.path.join(base_dir, "output_charts")

    if not os.path.exists(DATA_PATH):
        print(f"Error: Could not find {DATA_PATH}")
        sys.exit(1)

    print(f"Loading data from {DATA_PATH}...")
    data = loader.load_data(DATA_PATH)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    year = max(map(lambda row: row["Year"], data))

    print("Generating International Charts...")
    fig, (ax1, ax2) = tools.subplots(1, 2, figsize=(16, 8))
    plot_international_pie(ax1, data, year)
    plot_international_bar(ax2, data, year)
    fig.suptitle(f"International Analysis ({year})", fontsize=16)
    
    save_path = os.path.join(OUTPUT_DIR, "International_Report.png")
    fig.savefig(save_path)
    tools.close(fig)

    for region in valid_regions:
        print(f"Generating charts for {region}...")
        fig, (ax1, ax2) = tools.subplots(1, 2, figsize=(16, 8))
        
        plot_regional_histogram(ax1, data, region, year)
        plot_regional_line(ax2, data, region)
        fig.suptitle(f"Regional Analysis: {region}", fontsize=16)
        
        save_path = os.path.join(OUTPUT_DIR, f"{region}_Report.png")
        fig.savefig(save_path)
        tools.close(fig)

    print("Success: All images generated in /output_charts")
