import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons


class ConsoleWriter:
    """
    Outputs analysis results to the console as formatted text.
    Satisfies the DataSink protocol (has a write method).
    """

    def write(self, title, records):
        print("\n" + "=" * 60)
        print("  " + title)
        print("=" * 60)

        if not records:
            print("  No data found.")
            return

        # print each record as a simple line
        for i, record in enumerate(records, 1):
            parts = []
            for key, value in record.items():
                # format large numbers with commas
                if isinstance(value, float) and value > 1000:
                    parts.append(key + ": $" + "{:,.0f}".format(value))
                else:
                    parts.append(key + ": " + str(value))

            print("  " + str(i) + ". " + " | ".join(parts))

        print()


class GraphicsChartWriter:
    """
    Outputs analysis results as the original interactive dashboard.
    Satisfies the DataSink protocol (has a write method).
    Reuses the same dashboard from Phase 1 (src/dashboard.py).
    """

    # valid regions for the dashboard
    valid_regions = [
        "Africa", "Asia", "Europe",
        "North America", "South America", "Oceania",
    ]

    # aggregate entries to exclude from bar charts
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
        "West Bank and Gaza",
    }

    def write(self, title, records):
        """Creates the interactive dashboard with the full dataset."""
        if not records:
            print("  No data to chart.")
            return

        data = records
        regions = self._get_all_regions(data)
        year = self._get_latest_year(data)
        self._create_dashboard(data, regions, year)

    # ── Helper functions (same as src/processor.py) ──

    def _filter_by_region(self, data, region_name):
        return [row for row in data if row["Region"] == region_name]

    def _filter_by_year(self, data, year):
        return [row for row in data if row["Year"] == year]

    def _get_values(self, data):
        return [row["Value"] for row in data]

    def _calculate_sum(self, values):
        if not values:
            return 0.0
        return sum(values)

    def _calculate_average(self, values):
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _get_all_regions(self, data):
        all_regions = set(map(lambda row: row["Region"], data))
        return sorted(filter(lambda r: r in self.valid_regions, all_regions))

    def _get_latest_year(self, data):
        return max(map(lambda row: row["Year"], data))

    # ── Chart functions (same as src/dashboard.py) ──

    def _plot_regional_histogram(self, ax, data, region, year):
        ax.clear()
        ax.set_aspect("auto")
        ax.set_frame_on(True)

        region_data = self._filter_by_region(data, region)

        # Special condition: if Asia is selected, show Pakistan
        if region == "Asia":
            top_country = "Pakistan"
        else:
            year_data = self._filter_by_year(region_data, year)
            year_data = list(
                filter(lambda row: row["Country"] not in self.NON_COUNTRY_NAMES, year_data)
            )
            if len(year_data) == 0:
                ax.text(0.5, 0.5, "No data", ha="center", va="center")
                return
            top_country = max(year_data, key=lambda x: x["Value"])["Country"]

        country_data = list(filter(lambda row: row["Country"] == top_country, region_data))
        country_data = sorted(country_data, key=lambda x: x["Year"])

        years = list(map(lambda row: row["Year"], country_data))
        values = list(map(lambda row: row["Value"] / 1e9, country_data))

        ax.bar(years, values, color="#4CAF50", alpha=0.7, edgecolor="black", width=0.8)
        ax.set_title("GDP Growth - " + top_country)
        ax.set_xlabel("Year")
        ax.set_ylabel("GDP (Billion $)")
        ax.grid(True, axis="both", linestyle="--", alpha=0.5)

        ax.text(
            0.03, 0.95, "Current GDP: $" + str(int(country_data[-1]["Value"])),
            transform=ax.transAxes, fontsize=8, fontweight="bold",
            va="top", ha="left",
        )

    def _plot_regional_line(self, ax, data, region):
        ax.clear()
        ax.set_aspect("auto")

        region_data = self._filter_by_region(data, region)
        years_set = sorted(set(map(lambda row: row["Year"], region_data)))

        calc_year_total = (
            lambda y: self._calculate_sum(
                self._get_values(self._filter_by_year(region_data, y))
            )
            / 1000000000000
        )

        gdp_per_year = list(map(calc_year_total, years_set))

        ax.plot(years_set, gdp_per_year, marker=".", linewidth=2, color="#4CAF50")
        ax.set_title("GDP Trend - " + region)
        ax.set_xlabel("Year")
        ax.set_ylabel("GDP (Trillion $)")
        ax.grid(True, axis="both", linestyle="--", alpha=0.5)

    def _plot_international_pie(self, ax, data, year):
        ax.clear()
        ax.set_frame_on(True)

        year_data = self._filter_by_year(data, year)

        region_totals = list(filter(
            lambda x: x[1] > 0,
            map(lambda r: (r, self._calculate_sum(self._get_values(self._filter_by_region(year_data, r)))), self.valid_regions),
        ))

        if not region_totals:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            return

        region_names = list(map(lambda x: x[0], region_totals))
        region_values = list(map(lambda x: x[1], region_totals))

        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F"]

        wedges = ax.pie(
            region_values, colors=colors, startangle=140,
            autopct="%1.1f%%", textprops={"fontsize": 6},
        )[0]
        ax.set_title("Regional GDP Distribution (" + str(year) + ")")
        ax.legend(
            wedges, region_names, loc="upper center",
            bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=7,
            handlelength=1, handleheight=1,
        )

    def _plot_international_bar(self, ax, data, year):
        ax.clear()
        ax.set_aspect("auto")

        year_data = self._filter_by_year(data, year)
        year_data = list(
            filter(lambda row: row["Country"] not in self.NON_COUNTRY_NAMES, year_data)
        )

        if len(year_data) == 0:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
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

    # ── The interactive dashboard (same as src/dashboard.py) ──

    def _create_dashboard(self, data, regions, year):
        fig = plt.figure(figsize=(16, 8))

        ax1 = plt.subplot(1, 2, 1)
        ax2 = plt.subplot(1, 2, 2)
        ax1.set_position([0.20, 0.15, 0.35, 0.70])
        ax2.set_position([0.60, 0.15, 0.35, 0.70])

        fig.text(
            0.5, 0.96, "GDP ANALYSIS DASHBOARD",
            ha="center", fontsize=16, fontweight="bold"
        )

        options = ["International"] + regions
        state = {"region": "International"}

        region_ax = plt.axes([0.02, 0.35, 0.12, 0.45])
        region_radio = RadioButtons(region_ax, options)
        region_ax.set_title("Select Region", fontweight="bold")

        # separator line under first option
        num_options = len(options)
        separator_y = 1 - (1.2 / num_options)
        region_ax.plot(
            [0, 1], [separator_y, separator_y],
            color="black", linewidth=1, transform=region_ax.transAxes,
        )

        stats_avg = fig.text(0.08, 0.28, "", fontsize=11, fontweight="bold", va="top", ha="center")
        stats_total = fig.text(0.08, 0.18, "", fontsize=11, fontweight="bold", va="top", ha="center")

        def update_stats():
            current = state["region"]
            latest = self._get_latest_year(data)
            source = data if current == "International" else self._filter_by_region(data, current)
            year_data = self._filter_by_year(source, latest)
            year_data = list(filter(lambda row: row["Country"] not in self.NON_COUNTRY_NAMES, year_data))
            vals = self._get_values(year_data)
            total = self._calculate_sum(vals)
            avg = self._calculate_average(vals)
            stats_avg.set_text("Avg GDP:\n$" + str(int(avg)))
            stats_total.set_text("Sum of GDP:\n$" + str(int(total)))

        def update_charts():
            current = state["region"]
            if current == "International":
                self._plot_international_pie(ax1, data, year)
                self._plot_international_bar(ax2, data, year)
            else:
                self._plot_regional_histogram(ax1, data, current, year)
                self._plot_regional_line(ax2, data, current)
            update_stats()
            fig.canvas.draw_idle()

        def on_region_change(label):
            state["region"] = label
            update_charts()

        region_radio.on_clicked(on_region_change)
        update_charts()
        plt.show()
