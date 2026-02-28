"""
Structural Code — Auto-generated from architecture.puml
These are the class skeletons matching the architecture diagram.
The actual implementations are in core/ and plugins/.
"""

from typing import Protocol, List, Any, runtime_checkable


# ═══════════════════════════════════════
#  CORE MODULE — contracts.py
# ═══════════════════════════════════════

@runtime_checkable
class DataSink(Protocol):
    """Outbound: Core calls this to output results."""
    def write(self, title: str, records: List[dict]) -> None: ...


class PipelineService(Protocol):
    """Inbound: Input module calls this to send data to Core."""
    def execute(self, raw_data: List[Any]) -> None: ...


# ═══════════════════════════════════════
#  CORE MODULE — engine.py
# ═══════════════════════════════════════

class TransformationEngine:
    """Implements PipelineService. Uses injected DataSink."""

    def __init__(self, sink: DataSink, config: dict):
        self.sink = sink
        self.config = config

    def execute(self, raw_data: List[Any]) -> None:
        ...  # dispatches to analysis functions

    def _run_top_10(self, data, params): ...
    def _run_bottom_10(self, data, params): ...
    def _run_growth_rate(self, data, params): ...
    def _run_avg_gdp(self, data, params): ...
    def _run_global_trend(self, data, params): ...
    def _run_fastest_growing(self, data, params): ...
    def _run_decline(self, data, params): ...
    def _run_contribution(self, data, params): ...


# ═══════════════════════════════════════
#  PLUGINS MODULE — inputs.py
# ═══════════════════════════════════════

class CSVReader:
    """Reads CSV, satisfies nothing — calls PipelineService.execute()."""

    def __init__(self, service: PipelineService, filepath: str):
        self.service = service
        self.filepath = filepath

    def run(self) -> None:
        ...  # read CSV → clean → self.service.execute(data)


class JSONReader:
    """Reads JSON, satisfies nothing — calls PipelineService.execute()."""

    def __init__(self, service: PipelineService, filepath: str):
        self.service = service
        self.filepath = filepath

    def run(self) -> None:
        ...  # read JSON → self.service.execute(data)


# ═══════════════════════════════════════
#  PLUGINS MODULE — outputs.py
# ═══════════════════════════════════════

class ConsoleWriter:
    """Satisfies DataSink — prints to console."""

    def write(self, title: str, records: List[dict]) -> None:
        ...  # print formatted text


class GraphicsChartWriter:
    """Satisfies DataSink — shows matplotlib charts."""

    def write(self, title: str, records: List[dict]) -> None:
        ...  # render bar/line/pie chart
