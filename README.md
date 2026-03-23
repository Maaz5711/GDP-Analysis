# SDA Project Phase 3: Generic Concurrent Real-Time Pipeline

## 📌 Project Overview
This project is Phase 3 of the SDA pipeline system.  
The goal is to move from a dataset-specific script to a fully **generic, configuration-driven, concurrent pipeline**.

The system no longer hardcodes dataset structure. Instead, it dynamically reads an unseen CSV using `config.json`, processes packets in parallel using Python `multiprocessing`, verifies authenticity using PBKDF2 hashing, and visualizes live queue health + data output in real time.

## 🎯 Phase 3 Objective
Build a reusable pipeline that can ingest and process unseen domains (for example Climate Data, Health Metrics, etc.) without changing the Input/Core/Output module source code.

The pipeline is controlled by:
- Schema mapping (`source_name` -> `internal_mapping`)
- Type casting (`string`, `integer`, `float`)
- Runtime dynamics (input speed, core worker count, queue sizes)
- Processing settings (hash verification + running average)
- Dashboard settings (telemetry visibility + chart bindings)

## 🏗️ Architectural Design
The project follows a clean 3-module pipeline plus an orchestrator:

- **Main Module (`main.py`)**  
  The orchestrator. Loads `config.json`, creates bounded queues, starts worker processes, and launches dashboard + telemetry wiring.

- **Input Module (`plugins/inputs.py`)**  
  Reads CSV rows, maps external column names to generic internal packet fields, and casts values to configured primitive types.

- **Core Module (`Core/engine.py`)**  
  Performs all processing:
  - Stateless parallel signature verification workers (`SignatureVerifier`)
  - Stateful stream re-sequencing + sliding running average (`Aggregator`)

- **Output Module (`plugins/outputs.py`)**  
  Implements Observer pattern for runtime monitoring:
  - `PipelineTelemetry` = Subject (polls queue levels)
  - `Dashboard` = Observer (renders queue pressure + live charts)

## ⚙️ Concurrency and Stream Model
The pipeline uses a Producer-Consumer model with bounded `multiprocessing.Queue` streams:

1. **Raw Data Stream**: Input -> Core Verifiers (`raw_queue`)
2. **Intermediate Stream**: Verifiers -> Aggregator (`verified_queue`)
3. **Processed Stream**: Aggregator -> Dashboard (`processed_queue`)

Because queues are bounded, backpressure is automatic: if Core is slower than Input, queue fill levels rise and naturally throttle upstream producers.

## 🔐 Processing Logic
### 1) Stateless authentication (parallel)
Each verifier worker:
- Reads packet from `raw_queue`
- Recomputes PBKDF2-HMAC signature from `metric_value` + `secret_key`
- Compares against packet `security_hash`
- Forwards valid packets
- Marks invalid packets as dropped

### 2) Stateful stream aggregation (single node)
Aggregator:
- Re-sequences packets using `_seq`
- Maintains sliding window
- Computes `computed_metric` running average
- Emits ordered processed packets to output stream

## 👁️ Observer-Based Telemetry
`PipelineTelemetry` independently polls queue `qsize()` and notifies dashboard subscribers.

Dashboard renders:
- Color-coded queue bars  
  - Green: smooth flow  
  - Yellow: filling  
  - Red: heavy backpressure
- Real-time value chart
- Real-time running-average chart

## 📂 Project Structure

```text
project_root/
│
├── main.py                # Orchestrator / entry point
├── config.json            # Full pipeline configuration
├── README.md              # Project documentation (optional GitHub default)
├── readme.MD              # This documentation file
├── readme.txt             # TA quick-start instructions
│
├── Core/
│   ├── __init__.py
│   └── engine.py          # Signature verifier + aggregator logic
│
├── plugins/
│   ├── __init__.py
│   ├── inputs.py          # Generic CSV ingestion + schema mapping
│   └── outputs.py         # Telemetry subject + dashboard observer
│
└── data/
    ├── sample_sensor_data.csv
    └── new.csv            # Alternate unseen-style test dataset
```

## 🚀 How to Run
1. Install dependency:

`pip install matplotlib`

2. Run full dashboard mode:

`python main.py`

3. Run terminal-only mode (no GUI):

`python main.py --stream-test`

## 🧪 Testing with Unseen Datasets
To test true generic behavior:

1. Add a new CSV file in `data\` (or any path).
2. Update `config.json`:
   - `dataset_path`
   - `schema_mapping.columns`
   - visualization axis mappings
3. Keep processing settings aligned with the dataset signature format.
4. Run `python main.py`.

## ✅ Deliverable Notes (TA Use)
- Main executable file: `main.py`
- Config file location: project root (`config.json`)
- Dataset location: usually `data\...` (or any path referenced by config)
- No hardcoded domain assumptions in Input/Core/Output modules
- Hash algorithm is fixed to `pbkdf2_hmac` per project requirement
