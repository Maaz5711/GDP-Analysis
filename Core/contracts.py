from typing import Protocol, runtime_checkable


@runtime_checkable
class DataSink(Protocol):
    #Any output must have this method.
    def write(self, title: str, records: list[dict]) -> None: ...


@runtime_checkable
class PipelineService(Protocol):
    #The engine must have this method so input readers can call it.
    def execute(self, raw_data: list) -> None: ...
