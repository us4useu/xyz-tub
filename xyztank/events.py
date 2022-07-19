from abc import ABC
from dataclasses import dataclass


class Event(ABC):
    pass


@dataclass(frozen=True)
class StartMeasurementEvent(Event):
    settings: str


@dataclass(frozen=True)
class SaveMeasurementEvent(Event):
    output: str


@dataclass(frozen=True)
class StopMeasurementEvent(Event):
    pass


@dataclass(frozen=True)
class ExitApplicationEvent:
    pass