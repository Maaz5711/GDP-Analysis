import csv
import time

TYPE_CASTERS = {
    "string": str,
    "integer": int,
    "float": float,
}

class InputProducer:
    # This module only reads rows and standardizes packet shape/types.
    def __init__(self, config):
        self.dataset_path = config["dataset_path"]
        self.columns = config["schema_mapping"]["columns"]
        self.delay = config["pipeline_dynamics"]["input_delay_seconds"]

    def run(self, raw_queue, num_workers):
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for seq, row in enumerate(reader):
                packet = self._map_row(row, seq)
                raw_queue.put(packet)
                time.sleep(self.delay)

        # One sentinel per verifier worker.
        for _ in range(num_workers):
            raw_queue.put(None)

    def _map_row(self, row, seq):
        packet = {"_seq": seq}
        for col in self.columns:
            raw_value = row[col["source_name"]]
            caster = TYPE_CASTERS[col["data_type"]]
            packet[col["internal_mapping"]] = caster(raw_value)
        return packet
