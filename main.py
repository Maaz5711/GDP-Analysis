import json
import multiprocessing
import sys
import time
from queue import Empty
from plugins.inputs import InputProducer
from Core.engine import SignatureVerifier, Aggregator
from plugins.outputs import PipelineTelemetry, Dashboard

def run_input(config, raw_queue, num_workers):
    producer = InputProducer(config)
    producer.run(raw_queue, num_workers)

def run_verifier(config, raw_queue, verified_queue):
    verifier = SignatureVerifier(config)
    verifier.run(raw_queue, verified_queue)

def run_aggregator(config, num_workers, verified_queue, processed_queue):
    aggregator = Aggregator(config, num_workers)
    aggregator.run(verified_queue, processed_queue)

# Simple non-GUI mode to observe queue behavior from the terminal.
def run_stream_probe(config, frames=200, poll_interval=0.2, drain_batch=2):
    max_size = config["pipeline_dynamics"]["stream_queue_max_size"]
    num_workers = config["pipeline_dynamics"]["core_parallelism"]

    raw_queue = multiprocessing.Queue(maxsize=max_size)
    verified_queue = multiprocessing.Queue(maxsize=max_size)
    processed_queue = multiprocessing.Queue(maxsize=max_size)

    procs = [multiprocessing.Process(target=run_input, args=(config, raw_queue, num_workers))]
    for _ in range(num_workers):
        procs.append(multiprocessing.Process(target=run_verifier, args=(config, raw_queue, verified_queue)))
    procs.append(
        multiprocessing.Process(target=run_aggregator, args=(config, num_workers, verified_queue, processed_queue))
    )

    for proc in procs:
        proc.start()

    total = 0
    for frame in range(frames):
        raw_level = raw_queue.qsize()
        ver_level = verified_queue.qsize()
        proc_level = processed_queue.qsize()
        if frame % 5 == 0:
            print(
                f"Frame {frame:3d} | raw={raw_level:2d}  verified={ver_level:2d}  "
                f"processed={proc_level:2d}  | total_read={total}"
            )

        for _ in range(drain_batch):
            try:
                packet = processed_queue.get_nowait()
            except Empty:
                break
            if packet is None:
                print(f"Done at frame {frame}, total: {total}")
                for proc in procs:
                    proc.join(timeout=2)
                return
            total += 1

        time.sleep(poll_interval)

if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    if "--stream-test" in sys.argv:
        run_stream_probe(config)
        raise SystemExit(0)

    max_size = config["pipeline_dynamics"]["stream_queue_max_size"]
    num_workers = config["pipeline_dynamics"]["core_parallelism"]

    # Bounded queues create natural backpressure in the pipeline.
    raw_queue = multiprocessing.Queue(maxsize=max_size)
    verified_queue = multiprocessing.Queue(maxsize=max_size)
    processed_queue = multiprocessing.Queue(maxsize=max_size)

    input_proc = multiprocessing.Process(
        target=run_input, args=(config, raw_queue, num_workers),
    )

    verifier_procs = []
    for _ in range(num_workers):
        p = multiprocessing.Process(
            target=run_verifier, args=(config, raw_queue, verified_queue),
        )
        verifier_procs.append(p)

    agg_proc = multiprocessing.Process(
        target=run_aggregator, args=(config, num_workers, verified_queue, processed_queue),
    )

    input_proc.start()
    for p in verifier_procs:
        p.start()
    agg_proc.start()

    # Dashboard stays in main process while workers run in background.
    telemetry = PipelineTelemetry(
        {"raw": raw_queue, "verified": verified_queue, "processed": processed_queue},
        max_size,
    )

    dashboard = Dashboard(config, processed_queue, telemetry)
    dashboard.run()

    # Try a clean shutdown first, then force-stop any stuck worker.
    all_procs = [input_proc, agg_proc] + verifier_procs
    for p in all_procs:
        p.join(timeout=2)
    for p in all_procs:
        if p.is_alive():
            p.terminate()
