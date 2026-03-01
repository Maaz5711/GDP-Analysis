import json
from Core.engine import TransformationEngine
from plugins.inputs import CSVReader, JSONReader
from plugins.outputs import ConsoleWriter, GraphicsChartWriter

# maps config strings to actual classes
INPUT_DRIVERS = {
    "csv": CSVReader,
    "json": JSONReader,
}

OUTPUT_DRIVERS = {
    "console": ConsoleWriter,
    "chart": GraphicsChartWriter,
}


def bootstrap():
    # load config
    with open("config.json", "r") as f:
        config = json.load(f)

    # create the output writer
    output_type = config["output"]["type"]
    SinkClass = OUTPUT_DRIVERS[output_type]
    sink = SinkClass()

    # create the engine and inject the sink into it
    engine = TransformationEngine(sink, config)

    # create the input reader and inject the engine into it
    input_type = config["input"]["type"]
    input_path = config["input"]["path"]
    ReaderClass = INPUT_DRIVERS[input_type]
    reader = ReaderClass(engine, input_path)

    # run the pipeline
    reader.run()

    # if using charts, show them
    if hasattr(sink, "show"):
        sink.show()


if __name__ == "__main__":
    bootstrap()
