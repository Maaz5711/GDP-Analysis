import hashlib

# Signature is built from metric value + secret key using PBKDF2.
def verify_signature(metric_value, security_hash, secret_key, iterations):
    raw_value_str = "{:.2f}".format(metric_value)
    computed_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password=secret_key.encode("utf-8"),
        salt=raw_value_str.encode("utf-8"),
        iterations=iterations,
    ).hex()
    return computed_hash == security_hash

def compute_average(window):
    return sum(window) / len(window) if window else 0.0

class SignatureVerifier:
    def __init__(self, config):
        task = config["processing"]["stateless_tasks"]
        if task["algorithm"] != "pbkdf2_hmac":
            raise ValueError("Only pbkdf2_hmac is supported by this pipeline.")
        self.secret_key = task["secret_key"]
        self.iterations = task["iterations"]

    def run(self, raw_queue, verified_queue):
        # This worker stays stateless so many copies can run in parallel.
        while True:
            packet = raw_queue.get()
            if packet is None:
                verified_queue.put(None)
                break

            is_valid = verify_signature(
                packet["metric_value"],
                packet["security_hash"],
                self.secret_key,
                self.iterations,
            )

            if is_valid:
                verified_queue.put(packet)
            else:
                verified_queue.put({"_seq": packet["_seq"], "_dropped": True})

class Aggregator:
    def __init__(self, config, num_workers):
        task = config["processing"]["stateful_tasks"]
        self.window_size = task["running_average_window_size"]
        self.num_workers = num_workers
        self.window = []
        self.buffer = {}
        self.next_seq = 0

    def run(self, verified_queue, processed_queue):
        # Aggregator is the single ordered point in the pipeline.
        sentinels_received = 0

        while True:
            packet = verified_queue.get()

            if packet is None:
                sentinels_received += 1
                if sentinels_received >= self.num_workers:
                    self._flush_buffer(processed_queue)
                    processed_queue.put(None)
                    break
                continue

            self.buffer[packet["_seq"]] = packet
            self._flush_buffer(processed_queue)

    def _flush_buffer(self, processed_queue):
        # Emit only contiguous sequence numbers to keep stream order.
        while self.next_seq in self.buffer:
            packet = self.buffer.pop(self.next_seq)
            self.next_seq += 1

            if packet.get("_dropped"):
                continue

            self.window.append(packet["metric_value"])
            if len(self.window) > self.window_size:
                self.window.pop(0)

            packet["computed_metric"] = compute_average(self.window)
            processed_queue.put(packet)
