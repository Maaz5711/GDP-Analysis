import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons


class ConsoleWriter:
    # Prints analysis results to the terminal.

    def write(self, title, records):
        print("\n" + "=" * 60)
        print("  " + title)
        print("=" * 60)

        if not records:
            print("  No data found.")
            return

        for i, record in enumerate(records, 1):
            parts = []
            for key, value in record.items():
                if isinstance(value, float) and value > 1000:
                    parts.append(key + ": $" + "{:,.0f}".format(value))
                else:
                    parts.append(key + ": " + str(value))
            print("  " + str(i) + ". " + " | ".join(parts))

        print()


class GraphicsChartWriter:
    # Shows all analysis results in one window.
    # Radio buttons on the left let the user switch between charts.
    

    def __init__(self):
        self.results = []

    def write(self, title, records):
        # just store the results for now, we draw them in show()
        self.results.append({"title": title, "records": records})

    def show(self):
        if not self.results:
            return

        fig = plt.figure(figsize=(16, 8))

        fig.text(0.55, 0.96, "GDP ANALYSIS DASHBOARD",
                 ha="center", fontsize=16, fontweight="bold")

        # radio buttons on the left side
        option_labels = ["Option " + str(i + 1) for i in range(len(self.results))]

        radio_ax = fig.add_axes([0.01, 0.25, 0.10, 0.55])
        radio_ax.set_title("Select\nAnalysis", fontweight="bold", fontsize=9)
        radio = RadioButtons(radio_ax, option_labels, activecolor="#4CAF50")

        for label in radio.labels:
            label.set_fontsize(8)

        # this function picks the right chart type and draws it
        def draw_chart(index):
            # remove old chart (but keep the radio buttons)
            for a in fig.axes:
                if a is not radio_ax:
                    fig.delaxes(a)

            title = self.results[index]["title"]
            records = self.results[index]["records"]

            if not records:
                ax = fig.add_axes([0.18, 0.10, 0.78, 0.80])
                ax.text(0.5, 0.5, "No data found.", ha="center", va="center")
                ax.set_title(title, fontsize=13, fontweight="bold")
                ax.axis("off")
                fig.canvas.draw_idle()
                return

            if "Top 10" in title:
                draw_bar(title, records, "Country", "GDP", "#2196F3")
            elif "Bottom 10" in title:
                draw_bar(title, records, "Country", "GDP", "#FF5722")
            elif "Growth Rate" in title and "Continent" not in title:
                draw_horizontal_bar(title, records, "Country", "Growth Rate (%)", "#4CAF50")
            elif "Average GDP" in title:
                draw_bar(title, records, "Continent", "Average GDP", "#9C27B0")
            elif "Global GDP Trend" in title:
                draw_line(title, records, "Year", "Total Global GDP")
            elif "Fastest Growing" in title:
                draw_bar(title, records, "Continent", "Growth Rate (%)", "#FF9800")
            elif "Consistent" in title:
                draw_decline_bar(title, records)
            elif "Contribution" in title:
                draw_pie(title, records, "Continent", "Contribution (%)")

            fig.canvas.draw_idle()

        # chart drawing functions

        def draw_bar(title, records, label_key, value_key, color):
            ax = fig.add_axes([0.20, 0.18, 0.75, 0.70])

            labels = [str(r[label_key]) for r in records]
            values = [r[value_key] for r in records]

            # show GDP in billions for readability
            y_label = value_key
            if value_key in ("GDP", "Average GDP"):
                values = [v / 1e9 for v in values]
                y_label = value_key + " (Billion $)"

            bars = ax.bar(range(len(labels)), values, color=color,
                          alpha=0.8, edgecolor="black", width=0.6)

            ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
            ax.set_xlabel(label_key)
            ax.set_ylabel(y_label)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
            ax.grid(True, axis="y", linestyle="--", alpha=0.4)

            # put the value on top of each bar
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, height,
                            "{:,.0f}".format(height),
                            ha="center", va="bottom", fontsize=6)

        def draw_horizontal_bar(title, records, label_key, value_key, color):
            ax = fig.add_axes([0.28, 0.08, 0.67, 0.82])

            # only show top 20 so it's readable
            records = records[:20]
            labels = [str(r[label_key]) for r in records][::-1]
            values = [r[value_key] for r in records][::-1]

            bars = ax.barh(range(len(labels)), values, color=color,
                           alpha=0.8, edgecolor="black", height=0.6)

            ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
            ax.set_xlabel(value_key)
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels, fontsize=7)
            ax.grid(True, axis="x", linestyle="--", alpha=0.4)

            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height() / 2,
                        " " + str(round(width, 1)) + "%",
                        ha="left", va="center", fontsize=6)

        def draw_line(title, records, x_key, y_key):
            ax = fig.add_axes([0.20, 0.15, 0.75, 0.73])

            x = [r[x_key] for r in records]
            y = [r[y_key] / 1e12 for r in records]  # show in trillions

            ax.plot(x, y, marker="o", linewidth=2, color="#4CAF50", markersize=5)
            ax.fill_between(x, y, alpha=0.15, color="#4CAF50")

            ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
            ax.set_xlabel(x_key)
            ax.set_ylabel(y_key + " (Trillion $)")
            ax.grid(True, linestyle="--", alpha=0.4)

            # label the first and last points
            ax.annotate("{:,.1f}T".format(y[0]), (x[0], y[0]),
                        textcoords="offset points", xytext=(0, 10),
                        fontsize=8, ha="center")
            ax.annotate("{:,.1f}T".format(y[-1]), (x[-1], y[-1]),
                        textcoords="offset points", xytext=(0, 10),
                        fontsize=8, ha="center")

        def draw_pie(title, records, label_key, value_key):
            ax = fig.add_axes([0.22, 0.05, 0.70, 0.85])
            ax.set_aspect("equal")

            labels = [r[label_key] for r in records]
            values = [r[value_key] for r in records]
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F"]

            wedges, texts, autotexts = ax.pie(
                values, colors=colors, startangle=140,
                autopct="%1.1f%%", textprops={"fontsize": 9},
                pctdistance=0.75,
            )

            for t in autotexts:
                t.set_fontweight("bold")

            ax.set_title(title, fontsize=13, fontweight="bold", pad=15)
            ax.legend(wedges, labels, loc="lower center",
                      bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=9)

        def draw_decline_bar(title, records):
            if not records:
                ax = fig.add_axes([0.18, 0.10, 0.78, 0.80])
                ax.text(0.5, 0.5, "No declining countries found.",
                        ha="center", va="center", fontsize=14)
                ax.set_title(title, fontsize=13, fontweight="bold")
                ax.axis("off")
                return

            ax = fig.add_axes([0.20, 0.18, 0.75, 0.70])

            countries = [r["Country"] for r in records]
            keys = [k for k in records[0].keys() if k != "Country"]
            start_key = keys[0]
            end_key = keys[1]

            start_values = [r[start_key] / 1e9 for r in records]
            end_values = [r[end_key] / 1e9 for r in records]

            w = 0.35
            positions = list(range(len(countries)))

            ax.bar([p - w / 2 for p in positions], start_values, w,
                   label=start_key, color="#42A5F5", edgecolor="black")
            ax.bar([p + w / 2 for p in positions], end_values, w,
                   label=end_key, color="#EF5350", edgecolor="black")

            ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
            ax.set_xlabel("Country")
            ax.set_ylabel("GDP (Billion $)")
            ax.set_xticks(positions)
            ax.set_xticklabels(countries, rotation=30, ha="right", fontsize=9)
            ax.legend(fontsize=9)
            ax.grid(True, axis="y", linestyle="--", alpha=0.4)

        # when a radio button is clicked, redraw the chart

        def on_select(label):
            index = option_labels.index(label)
            draw_chart(index)

        radio.on_clicked(on_select)

        # show the first chart by default
        draw_chart(0)
        plt.show()
