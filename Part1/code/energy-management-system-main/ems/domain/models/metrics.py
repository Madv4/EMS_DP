from dataclasses import dataclass, field
from collections import deque
import uuid

from ems.domain.models.types import MetricKey


@dataclass(slots=True)
class Metrics:
    """Container for time series metrics, with a fixed
    duration (amount of time steps in the data)
    forward metrics are forcasts and plans,
    whereas backward metrics are actuals
    """

    entries: dict[MetricKey, object] = field(default_factory=dict)
    is_forward: bool = True
    duration: int = 24

    def __post_init__(self) -> None:
        self.initialize_all_metrics()

    # Initialization

    def initialize_all_metrics(self) -> None:
        self.initialize_source_metrics()
        self.initialize_load_metrics()

    def initialize_source_metrics(self) -> None:
        """Initialize all source metrics to zero"""
        for key in MetricKey.source_metrics():
            self.entries[key] = deque([0.0] * self.duration, maxlen=self.duration)

    def initialize_load_metrics(self) -> None:
        """Initialize empty load metric maps"""
        for key in MetricKey.load_metrics():
            self.entries[key] = {}

    def initialize_load(self, load_id: uuid.UUID) -> None:
        """Create zeroed time series for a load"""
        for key in MetricKey.load_metrics():
            self.entries[key][load_id] = deque(
                [0.0] * self.duration, maxlen=self.duration
            )

    def clear_load(self, load_id: uuid.UUID) -> None:
        """Reset an existing load's metrics to zero"""
        for key in MetricKey.load_metrics():
            if load_id in self.entries[key]:
                self.entries[key][load_id] = deque(
                    [0.0] * self.duration, maxlen=self.duration
                )

    # Mutation

    def enqueue_source_metric(self, key: MetricKey, value: float) -> None:
        if key in MetricKey.source_metrics():
            self.entries[key].append(value)

    def enqueue_load_metric(
        self, key: MetricKey, load_id: uuid.UUID, value: float
    ) -> None:
        if key in MetricKey.load_metrics():
            if load_id not in self.entries[key]:
                self.initialize_load(load_id)
            self.entries[key][load_id].append(value)

    def set_source_metric(self, key: MetricKey, values: list[float]) -> None:
        if key in MetricKey.source_metrics():
            self.entries[key] = deque(values, maxlen=self.duration)

    def set_load_metric(
        self, key: MetricKey, load_id: uuid.UUID, values: list[float]
    ) -> None:
        if key in MetricKey.load_metrics():
            self.entries[key][load_id] = deque(values, maxlen=self.duration)

    def set_load_metrics_bulk(
        self, key: MetricKey, items: dict[uuid.UUID, list[float]]
    ) -> None:
        if key in MetricKey.load_metrics():
            for load_id, value in items.items():
                self.entries[key][load_id] = deque(value, maxlen=self.duration)

    def remove_load(self, load_id: uuid.UUID) -> None:
        for key in MetricKey.load_metrics():
            self.entries[key].pop(load_id, None)

    # Query

    def get_source_metric(self, key: MetricKey) -> list[float]:
        return list(self.entries.get(key, []))

    def get_load_metric(self, key: MetricKey, load_id: uuid.UUID) -> list[float]:
        load_map = self.entries.get(key, {})
        return list(load_map.get(load_id, []))

    def get_load_metrics_bulk(self, key: MetricKey) -> dict[uuid.UUID, list[float]]:
        load_map = self.entries.get(key, {})
        return {load_id: list(values) for load_id, values in load_map.items()}
