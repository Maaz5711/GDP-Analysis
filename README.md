# SDA Project Phase 2: Modular Orchestration & Dependency Inversion

## 📌 Project Overview
This project is Phase 2 of a data-driven GDP analysis system built in Python. While Phase 1 focused on functional programming principles (using `map`, `filter`, `lambda`) and the Single Responsibility Principle (SRP), Phase 2 transitions the application into a robust **Modular Architecture** applying the **Dependency Inversion Principle (DIP)**.

The core objective is to completely decouple the business logic (Core) from data ingestion (Inputs) and data presentation (Outputs) using Python `typing.Protocol` and Dependency Injection.

## 🏗️ Architectural Design


The system is divided into four distinct logical packages. The **Core** acts as the authority, defining structural interfaces (Protocols) that external plugins must satisfy, ensuring data flows via duck typing without the Core ever knowing about specific file formats or UI frameworks.

* **Main Module (`main.py`)**: The Orchestrator. Parses `config.json`, acts as a Pythonic factory, and wires components together using Dependency Injection.
* **Core Module (`core/`)**: The Domain Engine. Contains all functional mathematical logic. Owns the `DataSink` and `PipelineService` protocols.
* **Input Module (`plugins/inputs.py`)**: The Source. Implements multiple readers (e.g., CSV, JSON) interacting purely via the Core's defined protocol.
* **Output Module (`plugins/outputs.py`)**: The Sink. Implements multiple writers (e.g., Console, GraphicsChart) that satisfy the `DataSink` protocol.

## 📊 Analytical Capabilities
The Core Engine computes the following configuration-driven metrics using functional programming:
* Top 10 / Bottom 10 Countries by GDP (for a given continent & year)
* GDP Growth Rate of each country (for a given continent & date range)
* Average GDP by Continent (for a given date range)
* Total Global GDP Trend (for a given date range)
* Fastest Growing Continent
* Countries with Consistent GDP Decline
* Continent Contribution to Global GDP

## 📂 Project Structure

```text
project_root/
│
├── main.py                # The Orchestrator / Entry Point
├── config.json            # Swappable configuration for pipelines and parameters
├── README.md              # Project documentation
│
├── core/
│   ├── __init__.py
│   ├── contracts.py       # Defines DataSink & PipelineService Protocols
│   └── engine.py          # TransformationEngine (Functional Math Logic)
│
├── plugins/
│   ├── __init__.py
│   ├── inputs.py          # CSVReader, JSONReader
│   └── outputs.py         # ConsoleWriter, GraphicsChartWriter
│
└── data/
    └── gdp_data.csv       # Raw source data
