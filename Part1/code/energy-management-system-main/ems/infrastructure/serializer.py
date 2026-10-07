from ems.domain.models.portfolio import Load, Portfolio
from ems.domain.models.metrics import Metrics
from fastapi.encoders import jsonable_encoder
from pydantic import TypeAdapter


LoadAdapter = TypeAdapter(Load)
PortfolioAdapter = TypeAdapter(Portfolio)
MetricsAdapter = TypeAdapter(Metrics)


def serial_portfolio(portfolio: Portfolio):
    return jsonable_encoder(portfolio)


def serial_metrics(metrics: Metrics):
    return jsonable_encoder(metrics)


def deserial_portfolio(data: dict) -> Portfolio:
    return PortfolioAdapter.validate_python(data)


def deserial_metrics(data: dict) -> Metrics:
    return MetricsAdapter.validate_python(data)
