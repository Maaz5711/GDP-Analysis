import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from queue import Empty

class PipelineTelemetry:
    # Subject in observer pattern: reads queue levels and notifies observers.
    def __init__(self, queues, max_size):
        self.queues = queues
        self.max_size = max_size
        self.observers = []

    def subscribe(self, observer):
        self.observers.append(observer)

    def poll_and_notify(self):
        levels = {}
        for name, queue in self.queues.items():
            levels[name] = queue.qsize()

        for observer in self.observers:
            observer.on_telemetry_update(levels)

class Dashboard:
    # Observer that renders telemetry + charts.
    def __init__(self, config, processed_queue, telemetry):
        self.config = config
        self.processed_queue = processed_queue
        self.telemetry = telemetry
        self.telemetry.subscribe(self)

        self.x_data = []
        self.y_values = []
        self.y_averages = []
        self.done = False

        self.levels = {"raw": 0, "verified": 0, "processed": 0}
        self.max_size = telemetry.max_size

    def on_telemetry_update(self, levels):
        self.levels = levels

    def run(self):
        charts = self.config["visualizations"]["data_charts"]
        telemetry_cfg = self.config["visualizations"]["telemetry"]

        # Top row for telemetry bars, bottom row for value/average charts.
        fig = plt.figure(figsize=(14, 8))
        fig.suptitle("Real-Time Pipeline Dashboard", fontsize=14, fontweight="bold")

        gs = fig.add_gridspec(2, 6, height_ratios=[1, 4], hspace=0.45, wspace=0.5)

        tel_axes = []
        tel_keys = []
        if telemetry_cfg.get("show_raw_stream"):
            tel_axes.append((fig.add_subplot(gs[0, 0:2]), "Raw Stream"))
            tel_keys.append("raw")
        if telemetry_cfg.get("show_intermediate_stream"):
            tel_axes.append((fig.add_subplot(gs[0, 2:4]), "Verified Stream"))
            tel_keys.append("verified")
        if telemetry_cfg.get("show_processed_stream"):
            tel_axes.append((fig.add_subplot(gs[0, 4:6]), "Processed Stream"))
            tel_keys.append("processed")

        ax_values = fig.add_subplot(gs[1, 0:3])
        ax_avg = fig.add_subplot(gs[1, 3:6])

        def update(frame):
            # Poll first, then consume a small batch of processed packets.
            self.telemetry.poll_and_notify()

            if not self.done:
                for _ in range(2):
                    try:
                        packet = self.processed_queue.get_nowait()
                    except Empty:
                        break

                    if packet is None:
                        self.done = True
                        break

                    self.x_data.append(packet[charts[0]["x_axis"]])
                    self.y_values.append(packet[charts[0]["y_axis"]])
                    self.y_averages.append(packet[charts[1]["y_axis"]])

            for i, (ax, label) in enumerate(tel_axes):
                self._draw_telemetry_bar(ax, label, self.levels.get(tel_keys[i], 0))

            self._draw_line(ax_values, charts[0]["title"], self.x_data, self.y_values, "#2196F3")
            self._draw_line(ax_avg, charts[1]["title"], self.x_data, self.y_averages, "#4CAF50")

        self.anim = FuncAnimation(fig, update, interval=200, cache_frame_data=False)
        plt.show()

    def _draw_telemetry_bar(self, ax, title, level):
        # Green/yellow/red indicates low/medium/high pressure.
        ax.clear()
        ratio = level / self.max_size if self.max_size > 0 else 0

        if ratio < 0.5:
            color = "#4CAF50"
        elif ratio < 0.8:
            color = "#FFC107"
        else:
            color = "#F44336"

        ax.barh([0], [1.0], color="#E0E0E0", height=0.5)
        ax.barh([0], [ratio], color=color, height=0.5)
        ax.set_xlim(0, 1)
        ax.set_title(title, fontsize=9, fontweight="bold")
        ax.set_yticks([])
        ax.set_xticks([])
        ax.text(0.5, 0, "{}/{}".format(level, self.max_size),
                ha="center", va="center", fontsize=8, fontweight="bold")

    def _draw_line(self, ax, title, x_data, y_data, color):
        # Draw one live line chart.
        ax.clear()
        if x_data and y_data:
            ax.plot(x_data, y_data, linewidth=1.2, color=color)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.tick_params(axis="x", rotation=30, labelsize=7)
