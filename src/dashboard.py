import matplotlib.pyplot as tools
from matplotlib.widgets import RadioButtons #used for the side menu
import processor

valid_regions = [
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "South America",
    "Oceania",
]

#to be excluded from the global bar chart
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

def get_all_regions(data):
    all_regions = set(map(lambda row: row["Region"], data))
    return sorted(filter(lambda r: r in valid_regions, all_regions))


def get_latest_year(data):
    return max(map(lambda row: row["Year"], data))

#the left graph in regional selection
def plot_regional_histogram(ax, data, region, year):
    ax.clear()
    ax.set_aspect("auto")
    ax.set_frame_on(True)

    region_data = processor.filter_by_region(data, region)

    # Special condition: if Asia is selected, show Pakistan
    if region == "Asia":
        top_country = "Pakistan"
    else:
        # Find the country with the biggest GDP in the current year
        year_data = processor.filter_by_year(region_data, year)
        year_data = list(
            filter(lambda row: row["Country"] not in NON_COUNTRY_NAMES, year_data)
        )

        if len(year_data) == 0:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            return

        top_country = max(year_data, key=lambda x: x["Value"])["Country"]

    # Get all years of GDP data for that country
    country_data = list(filter(lambda row: row["Country"] == top_country, region_data))
    country_data = sorted(country_data, key=lambda x: x["Year"])

    years = list(map(lambda row: row["Year"], country_data))
    values = list(map(lambda row: row["Value"] / 1e9, country_data))

    ax.bar(years, values, color="#4CAF50", alpha=0.7, edgecolor="black", width=0.8)
    ax.set_title("GDP Growth - " + top_country)
    ax.set_xlabel("Year")
    ax.set_ylabel("GDP (Billion $)")
    ax.grid(True, axis="both", linestyle="--", alpha=0.5)

    # Show current GDP of the displayed country in top left
    ax.text(
        0.03, 0.95, "Current GDP: $" + str(int(country_data[-1]["Value"])),
        transform=ax.transAxes, fontsize=8, fontweight="bold",
        va="top", ha="left",
    )

#the right one
def plot_regional_line(ax, data, region):
    ax.clear()
    ax.set_aspect("auto")

    region_data = processor.filter_by_region(data, region)

    years_set = sorted(set(map(lambda row: row["Year"], region_data)))

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

#uses the continents from the csv
def plot_international_pie(ax, data, year):
    ax.clear()
    ax.set_frame_on(True)

    year_data = processor.filter_by_year(data, year)

    region_totals = list(filter(
        lambda x: x[1] > 0,
        map(lambda r: (r, processor.calculate_sum(processor.get_values(processor.filter_by_region(year_data, r)))), valid_regions),
    ))

    if not region_totals:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        return

    region_names = list(map(lambda x: x[0], region_totals))
    region_values = list(map(lambda x: x[1], region_totals))

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

#displays the top gdp countries
def plot_international_bar(ax, data, year):
    ax.clear()
    ax.set_aspect("auto")

    year_data = processor.filter_by_year(data, year)
    year_data = list(
        filter(lambda row: row["Country"] not in NON_COUNTRY_NAMES, year_data)
    )

    if len(year_data) == 0:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        return

    # Sort by GDP and keep just the top 10
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

#the selective menu on the left
def create_dashboard(data, regions, year):
    fig = tools.figure(figsize=(16, 8))

    ax1 = tools.subplot(1, 2, 1)
    ax2 = tools.subplot(1, 2, 2)
    ax1.set_position([0.20, 0.15, 0.35, 0.70])
    ax2.set_position([0.60, 0.15, 0.35, 0.70])

    # Big title at the top
    fig.text(
        0.5, 0.96, "GDP ANALYSIS DASHBOARD", ha="center", fontsize=16, fontweight="bold"
    )

    options = ["International"] + regions

    state = {"region": "International"}

    region_ax = tools.axes([0.02, 0.35, 0.12, 0.45])
    region_radio = RadioButtons(region_ax, options)
    region_ax.set_title("Select Region", fontweight="bold")

    # Draw a separator line under the first option
    num_options = len(options)
    separator_y = 1 - (1.2 / num_options)
    region_ax.plot(
        [0, 1],
        [separator_y, separator_y],
        color="black",
        linewidth=1,
        transform=region_ax.transAxes,
    )

    # Stats text below the region selection buttons
    stats_avg = fig.text(0.08, 0.28, "", fontsize=11, fontweight="bold", va="top", ha="center")
    stats_total = fig.text(0.08, 0.18, "", fontsize=11, fontweight="bold", va="top", ha="center")

    def update_stats():
        current = state["region"]
        latest = get_latest_year(data)
        source = data if current == "International" else processor.filter_by_region(data, current)
        year_data = processor.filter_by_year(source, latest)
        year_data = list(filter(lambda row: row["Country"] not in NON_COUNTRY_NAMES, year_data))
        vals = processor.get_values(year_data)
        total = processor.calculate_sum(vals)
        avg = processor.calculate_average(vals)
        stats_avg.set_text("Avg GDP:\n$" + str(int(avg)))
        stats_total.set_text("Sum of GDP:\n$" + str(int(total)))

    # Swap charts based on the current selection
    def update_charts():
        current = state["region"]
        if current == "International":
            plot_international_pie(ax1, data, year)
            plot_international_bar(ax2, data, year)
        else:
            plot_regional_histogram(ax1, data, current, year)
            plot_regional_line(ax2, data, current)
        update_stats()
        fig.canvas.draw_idle()

    def on_region_change(label):
        state["region"] = label
        update_charts()

    #change the screen
    region_radio.on_clicked(on_region_change)
    update_charts()
    tools.show()
