"""
Main Module (The Orchestrator)
- Reads config.json
- Uses a dictionary factory to pick the right Input and Output classes
- Wires everything together using Dependency Injection
- Starts the pipeline
"""
import json
from core.engine import TransformationEngine
from plugins.inputs import CSVReader, JSONReader
from plugins.outputs import ConsoleWriter, GraphicsChartWriter


# ── Dictionary-based Factory (maps config strings to classes) ──

INPUT_DRIVERS = {
    "csv": CSVReader,
    "json": JSONReader,
}

OUTPUT_DRIVERS = {
    "console": ConsoleWriter,
    "chart": GraphicsChartWriter,
}


def bootstrap():
    """Load config, create components, wire them together, and run."""

    # 1. Load config
    with open("config.json", "r") as f:
        config = json.load(f)

    # 2. Create the Output (Sink)
    output_type = config["output"]["type"]
    SinkClass = OUTPUT_DRIVERS[output_type]
    sink = SinkClass()

    # 3. Create the Core Engine (inject the Sink)
    engine = TransformationEngine(sink, config)

    # 4. Create the Input Source (inject the Engine as the service)
    input_type = config["input"]["type"]
    input_path = config["input"]["path"]
    ReaderClass = INPUT_DRIVERS[input_type]
    reader = ReaderClass(engine, input_path)

    # 5. Run — data flows: Reader → Engine → Sink
    reader.run()


if __name__ == "__main__":
    bootstrap()