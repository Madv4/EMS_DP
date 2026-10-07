from pulp import PULP_CBC_CMD, LpProblem, LpVariable, lpSum, LpMinimize, LpStatusOptimal
from ems.application.solvers.base import (
    Parameters,
    LOAD_GRID_DRAW,
    LOAD_REN_DRAW,
    REN_SPILL,
)
from ems.domain.models.types import MetricKey

# Default engine
ENGINE = PULP_CBC_CMD(msg=False)


def _build(params: Parameters, model: LpProblem) -> tuple:
    loads = params.loads
    times = list(params.times)
    flow_min = params.flow_min
    flow_max = params.flow_max
    priority = params.priority
    start_opts = params.start_opts
    start_covers = params.start_covers
    is_confirmed = params.is_confirmed
    confirmed_activity = params.confirmed_activity
    grid_price = params.grid_price
    grid_co2 = params.grid_co2
    grid_prod = params.grid_prod
    ren_prod = params.ren_prod
    cost_vs_co2 = params.cost_vs_co2
    co2_coeff = params.co2_coeff
    prio_coeff = params.prio_coeff

    # decision variables
    start = LpVariable.dicts(
        "start",
        ((l, so) for l in loads if is_confirmed.get(l, 0) == 0 for so in start_opts[l]),
        cat="Binary",
    )
    grid_draw = LpVariable.dicts(
        LOAD_GRID_DRAW.value, ((l, t) for l in loads for t in times), lowBound=0
    )
    ren_draw = LpVariable.dicts(
        LOAD_REN_DRAW.value, ((l, t) for l in loads for t in times), lowBound=0
    )
    ren_spill = LpVariable.dicts(REN_SPILL.value, times, lowBound=0)

    # constraints per load / time
    for l in loads:
        if is_confirmed.get(l, 0) == 0:
            # ensure start exactly once for unconfirmed loads
            opts = start_opts.get(l, [])
            if opts:
                model += (
                    lpSum(start[l, so] for so in opts) == 1,
                    f"StartOnce_{l}",
                )

        for t in times:
            if is_confirmed.get(l, 0) == 1:
                eff_activity = confirmed_activity.get(l, [0] * len(times))[t]
            else:
                so_list = start_covers[l][t]
                eff_activity = lpSum(start[l, so] for so in so_list) if so_list else 0

            model += (
                grid_draw[l, t] + ren_draw[l, t] >= flow_min[l] * eff_activity,
                f"MinPowerFlow_{l}_{t}",
            )
            model += (
                grid_draw[l, t] + ren_draw[l, t] <= flow_max[l] * eff_activity,
                f"MaxPowerFlow_{l}_{t}",
            )

    # supply constraints per time
    for t in times:
        model += (
            lpSum(ren_draw[l, t] for l in loads) + ren_spill[t] == ren_prod[t],
            f"RenewableBalance_{t}",
        )
        model += (
            lpSum(grid_draw[l, t] for l in loads) <= grid_prod[t],
            f"GridLimit_{t}",
        )

    # objective
    total_cost = lpSum(grid_price[t] * grid_draw[l, t] for l in loads for t in times)
    total_co2 = lpSum(grid_co2[t] * grid_draw[l, t] for l in loads for t in times)

    priority_terms = []
    for l in loads:
        if is_confirmed.get(l, 0) == 0:
            # prefer earlier starts for higher priority loads
            priority_terms.append(
                lpSum(
                    priority[l] * (max(start_opts[l]) - so) * start[l, so]
                    for so in start_opts[l]
                )
            )
    priority_term = lpSum(priority_terms) if priority_terms else 0

    Z = (
        cost_vs_co2 * total_cost
        + (1 - cost_vs_co2) * co2_coeff * total_co2
        - prio_coeff * priority_term
    )
    model += Z
    return grid_draw, ren_draw, ren_spill


def _parse_output(params: Parameters, dvars: tuple) -> dict[MetricKey, object]:
    lgd_vars, lrd_vars, rs_vars = dvars
    times = list(params.times)

    load_grid_draw = {l: [lgd_vars[l, t].varValue for t in times] for l in params.loads}
    load_ren_draw = {l: [lrd_vars[l, t].varValue for t in times] for l in params.loads}
    ren_spill = [rs_vars[t].varValue for t in times]

    return {
        LOAD_GRID_DRAW: load_grid_draw,
        LOAD_REN_DRAW: load_ren_draw,
        REN_SPILL: ren_spill,
    }


def solve(params: Parameters) -> dict[MetricKey, object]:
    """MILP solver function"""

    model = LpProblem("MILP_Load_Scheduling", LpMinimize)
    dvars = _build(params, model)
    try:
        model.solve(ENGINE)
    except Exception:
        return {}
    if model.status == LpStatusOptimal:
        return _parse_output(params, dvars)
    return {}
