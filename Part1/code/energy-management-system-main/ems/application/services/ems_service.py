from ems.domain.models.types import LoadStatus
from ems.domain.models.portfolio import Portfolio
from ems.domain.models.metrics import Metrics
from ems.domain.ports.forecast_provider import ForecastProvider
from ems.domain.ports.portfolio_repository import PortfolioRepository

import ems.application.services.advance_metrics as advancer
import ems.application.services.deploy_plan as deployer
import ems.application.services.manage_portfolio as manager

from dataclasses import dataclass
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class EMSContext:
    """Runtime configuration and state for the EMS engine"""

    provider: ForecastProvider
    repository: PortfolioRepository

    portfolio: Portfolio
    forward: Metrics
    backward: Metrics


def boot(
    duration: int,
    provider: ForecastProvider,
    repository: PortfolioRepository,
):
    context = EMSContext(
        provider=provider,
        repository=repository,
        portfolio=Portfolio(),
        forward=Metrics(duration=duration),
        backward=Metrics(duration=duration, is_forward=False),
    )
    return context


def advance(context: EMSContext):
    advancer.next(
        context.portfolio, context.backward, context.forward, context.provider
    )
    plan(context)


def plan(context: EMSContext):
    if not context.portfolio.get_active_loads():
        return
    plan = deployer.generate_plan(context.portfolio, context.forward)
    if plan.success:
        deployer.apply_plan(plan, context.portfolio, context.forward)
    else:
        logger.warning(f"Plan generation failed: {plan.reason}, will retry soon")


def create_portfolio(context: EMSContext):
    portfolio = manager.create_portfolio(context.repository)
    context.portfolio = portfolio
    context.forward.initialize_all_metrics()
    context.backward.initialize_all_metrics()


def open_portfolio(context: EMSContext, folio_id: uuid.UUID):
    opened_portfolio = manager.open_portfolio(
        folio_id,
        context.repository,
    )
    context.portfolio = opened_portfolio
    context.forward.initialize_all_metrics()
    context.backward.initialize_all_metrics()
    for load_id in context.portfolio.loads.keys():
        context.forward.initialize_load(load_id)
        context.backward.initialize_load(load_id)


def patch_portfolio(
    context: EMSContext,
    cost_vs_emission_weight: Optional[float] = None,
    emission_coeff: Optional[float] = None,
    priority_coeff: Optional[float] = None,
):
    manager.patch_portfolio(
        context.portfolio,
        cost_vs_emission_weight,
        emission_coeff,
        priority_coeff,
        context.repository,
    )


def delete_portfolio(context: EMSContext, folio_id: uuid.UUID):
    if context.portfolio.folio_id == folio_id:
        logger.warning("Cannot delete an opened portfolio")
    else:
        manager.delete_portfolio(folio_id, context.repository)


def add_load(context: EMSContext):
    load = manager.add_load(context.portfolio, context.repository)
    context.forward.initialize_load(load.load_id)
    context.backward.initialize_load(load.load_id)
    return load


def patch_load(
    context: EMSContext,
    load_id: uuid.UUID,
    toggle: Optional[bool] = None,
    confirm: Optional[bool] = None,
    priority: Optional[int] = None,
    throughput: Optional[tuple] = None,
    run_duration: Optional[int] = None,
):
    load = manager.patch_load(
        context.portfolio,
        load_id,
        toggle,
        confirm,
        priority,
        throughput,
        run_duration,
        context.repository,
    )
    if load.status == LoadStatus.OFF:
        context.forward.clear_load(load_id)
    return load


def remove_load(context: EMSContext, load_id: uuid.UUID):
    manager.remove_load(context.portfolio, load_id, context.repository)
    context.backward.remove_load(load_id)
    context.forward.remove_load(load_id)
