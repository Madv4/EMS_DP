from enum import Enum


class LoadStatus(Enum):
    """Represents the operational status of energy loads in the system,
    and Used to track their lifecycle
    """

    OFF = "off"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    RUNNING = "running"


class MetricKey(Enum):
    """Energy system metrics for both forward (forecasted/planned)
    and backward (actual) measurements
    """

    GRID_PRICE = "grid_price"
    GRID_CO2 = "grid_co2"
    GRID_PROD = "grid_prod"
    REN_PROD = "ren_prod"

    LOAD_GRID_DRAW = "load_grid_draw"
    LOAD_REN_DRAW = "load_ren_draw"
    REN_SPILL = "ren_spill"

    @staticmethod
    def load_metrics():
        return {MetricKey.LOAD_GRID_DRAW, MetricKey.LOAD_REN_DRAW}

    @staticmethod
    def source_metrics():
        return {
            MetricKey.GRID_PRICE,
            MetricKey.GRID_CO2,
            MetricKey.GRID_PROD,
            MetricKey.REN_PROD,
            MetricKey.REN_SPILL,
        }

    @staticmethod
    def forecast_metrics():
        """contains all source metrics except for
        renewable spill which belongs to planning
        """
        return {
            MetricKey.GRID_PRICE,
            MetricKey.GRID_CO2,
            MetricKey.GRID_PROD,
            MetricKey.REN_PROD,
        }

    @staticmethod
    def plan_metrics():
        """contains all load metrics including
        renewable spill which is a derived metric
        """
        return {MetricKey.LOAD_GRID_DRAW, MetricKey.LOAD_REN_DRAW, MetricKey.REN_SPILL}
