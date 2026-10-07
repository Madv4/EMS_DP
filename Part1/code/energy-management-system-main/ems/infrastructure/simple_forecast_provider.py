from ems.domain.ports.forecast_provider import ForecastProvider
from ems.domain.models.types import MetricKey
import random


class SimpleForecastProvider(ForecastProvider):
    """Simple mock forecast provider for demo purposes"""

    def __init__(self):
        self.random = random.Random(42)  # Deterministic for demo

    def get_forecast_entry(self) -> dict[MetricKey, float]:
        return {
            MetricKey.GRID_PRICE: self.random.uniform(0.1, 0.3),
            MetricKey.GRID_CO2: self.random.uniform(0.2, 0.8),
            MetricKey.GRID_PROD: self.random.uniform(5.0, 15.0),
            MetricKey.REN_PROD: self.random.uniform(2.0, 8.0),
        }
