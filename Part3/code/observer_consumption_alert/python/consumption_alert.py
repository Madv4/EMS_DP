from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ConsumptionEvent:
    time_index: int
    by_load: dict[str, float]


class ConsumptionObserver(ABC):
    @abstractmethod
    def update(self, event: ConsumptionEvent) -> None:
        raise NotImplementedError


class ConsumptionSubject:
    def __init__(self):
        self._observers: list[ConsumptionObserver] = []

    def subscribe(self, observer: ConsumptionObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: ConsumptionObserver) -> None:
        self._observers.remove(observer)

    def notify(self, event: ConsumptionEvent) -> None:
        for observer in tuple(self._observers):
            observer.update(event)


@dataclass(frozen=True)
class AlertRecord:
    time_index: int
    load_id: str
    consumption: float
    threshold: float


class ConsumptionAlertObserver(ConsumptionObserver):
    def __init__(self, threshold: float = 10.0):
        self.alerts: list[AlertRecord] = []
        self.set_threshold(threshold)

    def set_threshold(self, threshold: float) -> None:
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        self.threshold = threshold

    def update(self, event: ConsumptionEvent) -> None:
        for load_id, consumption in event.by_load.items():
            if consumption > self.threshold:
                self.alerts.append(
                    AlertRecord(event.time_index, load_id, consumption, self.threshold)
                )

    def snapshot(self) -> list[dict]:
        return [asdict(alert) for alert in self.alerts]
