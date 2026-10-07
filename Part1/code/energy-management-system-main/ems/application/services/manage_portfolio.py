import uuid
from typing import Optional

from ems.domain.models.portfolio import Load, Portfolio
from ems.domain.ports.portfolio_repository import PortfolioRepository
from ems.domain.models.types import LoadStatus


def create_portfolio(repository: PortfolioRepository) -> Portfolio:
    """initializes or wipes and resets portfolio

    expected post-call behavior:
    must reset all metrics (backward and forward)
    """
    portfolio = Portfolio()
    repository.save_portfolio(portfolio)
    return portfolio


def open_portfolio(folio_id: uuid.UUID, repository: PortfolioRepository) -> Portfolio:
    """opens an in memory portfolio

    expected post-call behavior:
    must reset all metrics (backward and forward)
    all load metrics are cleared (all loads are off)
    """
    portfolio = repository.open_portfolio(folio_id)
    if portfolio is None:
        raise ValueError(f"Portfolio {folio_id} not found")
    portfolio.mark_dirty()  # needs planning
    return portfolio


def patch_portfolio(
    portfolio: Portfolio,
    cost_vs_emission_weight: Optional[float],
    emission_coeff: Optional[float],
    priority_coeff: Optional[float],
    repository: PortfolioRepository,
) -> None:
    """patches portfolio parameters"""
    if cost_vs_emission_weight is not None:
        _check_strict_unit_interval("cost vs emission weight", cost_vs_emission_weight)
        portfolio.cost_vs_emission_weight = cost_vs_emission_weight
    if emission_coeff is not None:
        _check_positive("emission_coeff", emission_coeff)
        portfolio.emission_coeff = emission_coeff
    if priority_coeff is not None:
        _check_positive("priority_coeff", priority_coeff)
        portfolio.priority_coeff = priority_coeff
    repository.save_portfolio(portfolio)
    portfolio.mark_dirty()


def delete_portfolio(folio_id, repository: PortfolioRepository) -> None:
    """deletes a portfolio directly on disk"""
    repository.delete_portfolio(folio_id)


def add_load(portfolio: Portfolio, repository: PortfolioRepository) -> Load:
    """adds new load to portfolio

    expected post-call behavior:
    must initialize this loads metrics
    """
    new = Load()
    portfolio.loads[new.load_id] = new
    repository.save_portfolio(portfolio)
    portfolio.mark_dirty()
    return new


def patch_load(
    portfolio: Portfolio,
    load_id: uuid.UUID,
    toggle: Optional[bool],
    confirm: Optional[bool],
    priority: Optional[int],
    throughput: Optional[tuple],
    run_duration: Optional[int],
    repository: PortfolioRepository,
) -> Load:
    """patches load parameters within portfolio

    expected post-call behavior:
    if the toggle off succeeds the loads 
    forward metrics must be cleared
    """
    if load_id not in portfolio.loads:
        raise ValueError(f"Load {load_id} not found")
    load = portfolio.loads[load_id]
    if toggle is not None:
        if toggle:
            load.toggle_on()
        else:
            load.toggle_off()
    if confirm is not None:
        if confirm:
            load.confirm_schedule()
        else:
            load.unconfirm_schedule()
    _check_running_constraints(load, (priority, throughput, run_duration))
    if priority is not None:
        _check_positive("priority", priority)
        load.priority = priority
    if throughput is not None:
        _check_valid_throughput(throughput)
        load.throughput = throughput
    if run_duration is not None:
        _check_positive("run_duration", run_duration)
        load.run_duration = run_duration
    repository.save_portfolio(portfolio)
    portfolio.mark_dirty()
    return load


def remove_load(
    portfolio: Portfolio, load_id: uuid.UUID, repository: PortfolioRepository
) -> None:
    """removes load within portfolio

    expected post-call behavior:
    must initialize this loads metrics
    """
    load = portfolio.loads.pop(load_id, None)
    if load is not None:
        repository.save_portfolio(portfolio)
        portfolio.mark_dirty()


# Helpers


def _check_strict_unit_interval(name, value):
    if not (0 < value < 1):
        raise ValueError(f"0 < {value} < 1 is not respected for {name}")


def _check_positive(name, value):
    if value <= 0:
        raise ValueError(f"0 < {value} is not respected for {name}")


def _check_valid_throughput(throughput):
    if not (0 < throughput[0] <= throughput[1]):
        raise ValueError(
            f"0 < {throughput[0]} <= {throughput[1]} is not respected for throughput"
        )


def _check_running_constraints(load: Load, patch: tuple):
    if load.status == LoadStatus.RUNNING:
        if any(x is not None for x in patch):
            raise ValueError(
                "Cannot modify throughput/run_duration/priority of a running load"
            )
