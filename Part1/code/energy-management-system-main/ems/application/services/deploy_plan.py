from ems.domain.models.portfolio import Portfolio
from ems.domain.models.metrics import Metrics
from ems.domain.models.plan import Plan
from ems.domain.models.types import LoadStatus

from ems.application.solvers.base import (
    LOAD_GRID_DRAW,
    LOAD_REN_DRAW,
    REN_SPILL,
    build_params,
)
import ems.application.solvers.milp_solver as primary
import ems.application.solvers.heuristic_solver as fallback


def generate_plan(portfolio: Portfolio, forward: Metrics) -> Plan:
    """Build parameters (will validate basic invariants)
    it tries the primary solver then uses fallback if needed
    """
    try:
        params = build_params(portfolio, forward)
    except Exception as exc:
        return Plan(success=False, reason=f"params_build_error: {exc}")

    updates = primary.solve(params)
    used_fallback = False
    if not updates:
        updates = fallback.solve(params)
        used_fallback = True
    # ensure expected keys are present for minimal sanity
    update_keys = updates.keys()
    if set(update_keys) != set({LOAD_GRID_DRAW, LOAD_REN_DRAW, REN_SPILL}):
        return Plan(success=False, reason="solver returned incomplete plan updates") 
    return Plan(success=True, used_fallback=used_fallback, updates=updates)


def apply_plan(plan: Plan, portfolio: Portfolio, forward: Metrics) -> None:
    """Applies the generated plan by updating forward metrics and
    transitioning portfolio load states accordingly
    """

    # Update forward metrics with plan decisions
    forward.set_load_metrics_bulk(LOAD_GRID_DRAW, plan.updates[LOAD_GRID_DRAW])
    forward.set_load_metrics_bulk(LOAD_REN_DRAW, plan.updates[LOAD_REN_DRAW])
    forward.set_source_metric(REN_SPILL, plan.updates[REN_SPILL])

    # Apply portfolio state transitions derived from the plan
    for load_id, load in portfolio.loads.items():
        g = plan.updates.get(LOAD_GRID_DRAW, {}).get(load_id, [0.0] * forward.duration)
        r = plan.updates.get(LOAD_REN_DRAW, {}).get(load_id, [0.0] * forward.duration)

        # scheduled activity vector and booleans
        scheduled = [(gi + ri) for gi, ri in zip(g, r)]
        any_scheduled = any(x > 0.0 for x in scheduled)
        running_now = scheduled[0] > 0.0

        # Start confirmed loads if scheduled to run now
        if load.status == LoadStatus.CONFIRMED and running_now:
            load.start_running()

        if not any_scheduled:
            load.toggle_off()

    portfolio.clear_dirty()
