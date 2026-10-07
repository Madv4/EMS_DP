from ems.domain.ports.forecast_provider import ForecastProvider
from ems.domain.models.types import MetricKey
from ems.domain.models.metrics import Metrics
from ems.domain.models.portfolio import Portfolio

import logging

logger = logging.getLogger(__name__)


def next(
    portfolio: Portfolio,
    backward: Metrics,
    forward: Metrics,
    forecast_provider: ForecastProvider,
) -> None:
    """Advances the simulation by one time step, rolling back stale forecasts
    to backward metrics and loading fresh forecasts into forward metrics
    """

    # get the required keys
    source_keys = MetricKey.source_metrics()
    load_keys = MetricKey.load_metrics()
    # get the currently running loads
    running = portfolio.get_running_loads().keys()
    # first rollback the backward metrics
    for key in source_keys:
        stale_forecast = forward.get_source_metric(key)
        val = stale_forecast[0] if len(stale_forecast) > 0 else 0.0
        backward.enqueue_source_metric(key, val)
    for key in load_keys:
        metrics = forward.get_load_metrics_bulk(key)
        for load_id, stale_schedule in metrics.items():
            if load_id in running:
                val = stale_schedule[0] if len(stale_schedule) > 0 else 0.0
                backward.enqueue_load_metric(key, load_id, val)
            else:
                backward.enqueue_load_metric(key, load_id, 0.0)

    # try to get the forecast
    try:
        forecast = forecast_provider.get_forecast_entry()
        forecast_provider.validate(forecast)
    except Exception as e:
        logger.warning(f"Forecast validation failed: {e}. Using zeros as fallback.")
        forecast = {
            key: 0.0 for key in MetricKey.source_metrics() if key != MetricKey.REN_SPILL
        }

    # next rollback the forward metrics
    for key in source_keys:
        if key == MetricKey.REN_SPILL:
            forward.enqueue_source_metric(key, 0.0)
        else:
            forward.enqueue_source_metric(key, forecast.get(key, 0.0))
    for key in load_keys:
        metrics = forward.get_load_metrics_bulk(key)
        for load_id in metrics.keys():
            forward.enqueue_load_metric(key, load_id, 0.0)
