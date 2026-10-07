from abc import ABC, abstractmethod
from ems.domain.models.types import MetricKey


class ForecastProvider(ABC):
    """Abstract interface for forecast metrics obtention"""

    @abstractmethod
    def get_forecast_entry(self) -> dict[MetricKey, float]:
        pass

    def validate(self, entry: dict[MetricKey, float]) -> None:
        """Must use this validation method on the
        get_forecast_entry() output before any further use
        """
        expected = MetricKey.forecast_metrics()
        if set(entry.keys()) != expected:
            raise ValueError(
                f"Improper source metrics for new forecast entry, expected: {expected}"
            )
