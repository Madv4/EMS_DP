from typing import Dict, List, Tuple
from ems.application.solvers.base import (
    Parameters,
    LOAD_GRID_DRAW,
    LOAD_REN_DRAW,
    REN_SPILL,
)

EPS = 1e-12


def _init_outputs(loads: List, T: int) -> Tuple[Dict, Dict]:
    load_grid_draw = {load: [0.0] * T for load in loads}
    load_ren_draw = {load: [0.0] * T for load in loads}
    return load_grid_draw, load_ren_draw


def _allocate_energy_to_load(
    required: float, available_ren: float, available_grid: float
) -> Tuple[float, float, bool]:
    """
    Allocate energy to meet requirement: renewables first, then grid
    Returns (renewable_used, grid_used, is_feasible)
    """
    renewable_used = min(required, available_ren)
    remaining_need = required - renewable_used

    grid_used = min(remaining_need, available_grid)
    remaining_need -= grid_used

    is_feasible = remaining_need <= EPS
    return renewable_used, grid_used, is_feasible


def _allocate_confirmed_loads(
    loads: List,
    T: int,
    is_confirmed: Dict,
    confirmed_activity: Dict,
    flow_min: Dict,
    flow_max: Dict,
    remaining_ren: List[float],
    remaining_grid: List[float],
    load_grid_draw: Dict,
    load_ren_draw: Dict,
) -> bool:
    """
    Two-pass allocation for confirmed loads:
      Pass 1: Ensure minima (ren first, then grid), else infeasible
      Pass 2: Top-up with remaining renewables toward flow_max (no grid top-up)
    """
    confirmed_loads = [load for load in loads if is_confirmed.get(load, 0) == 1]

    for load in confirmed_loads:
        activity = confirmed_activity.get(load, [0] * T)
        min_flow = float(flow_min[load])
        max_flow = float(flow_max[load])

        # Pass 1: meet minimum requirements
        for time_idx in range(T):
            if not activity[time_idx]:
                continue

            ren_used, grid_used, feasible = _allocate_energy_to_load(
                min_flow, remaining_ren[time_idx], remaining_grid[time_idx]
            )

            if not feasible:
                return False

            load_ren_draw[load][time_idx] += ren_used
            load_grid_draw[load][time_idx] += grid_used
            remaining_ren[time_idx] -= ren_used
            remaining_grid[time_idx] -= grid_used

        # Pass 2: top-up with remaining renewables
        for time_idx in range(T):
            if not activity[time_idx]:
                continue

            current_allocation = (
                load_ren_draw[load][time_idx] + load_grid_draw[load][time_idx]
            )
            available_capacity = max_flow - current_allocation

            if available_capacity > EPS and remaining_ren[time_idx] > EPS:
                additional_ren = min(available_capacity, remaining_ren[time_idx])
                load_ren_draw[load][time_idx] += additional_ren
                remaining_ren[time_idx] -= additional_ren

    return True


def _simulate_load_schedule(
    start_time: int,
    duration: int,
    min_flow: float,
    max_flow: float,
    remaining_ren: List[float],
    remaining_grid: List[float],
) -> Tuple[bool, List[float], List[float]]:
    """
    Simulate scheduling a load and return resource usage
    Returns (is_feasible, grid_usage_by_time, renewable_usage_by_time)
    """
    T = len(remaining_ren)
    end_time = start_time + duration

    # Work with copies to avoid mutating input
    sim_ren = remaining_ren[:]
    sim_grid = remaining_grid[:]
    grid_usage = [0.0] * T
    ren_usage = [0.0] * T

    # Allocate minimum requirements first
    for time_idx in range(start_time, end_time):
        ren_used, grid_used, feasible = _allocate_energy_to_load(
            min_flow, sim_ren[time_idx], sim_grid[time_idx]
        )

        if not feasible:
            return False, grid_usage, ren_usage

        ren_usage[time_idx] = ren_used
        grid_usage[time_idx] = grid_used
        sim_ren[time_idx] -= ren_used
        sim_grid[time_idx] -= grid_used

    # Top-up with available renewables
    for time_idx in range(start_time, end_time):
        current_flow = ren_usage[time_idx] + grid_usage[time_idx]
        available_capacity = max_flow - current_flow

        if available_capacity > EPS and sim_ren[time_idx] > EPS:
            additional_ren = min(available_capacity, sim_ren[time_idx])
            ren_usage[time_idx] += additional_ren
            sim_ren[time_idx] -= additional_ren

    return True, grid_usage, ren_usage


def _calculate_schedule_score(
    start_time: int,
    latest_start: int,
    grid_usage: List[float],
    grid_price: List[float],
    grid_co2: List[float],
    cost_vs_co2: float,
    co2_coeff: float,
    prio_coeff: float,
    load_priority: float,
) -> float:
    """Calculate the objective score for a schedule option"""
    total_cost = sum(price * usage for price, usage in zip(grid_price, grid_usage))
    total_co2 = sum(co2 * usage for co2, usage in zip(grid_co2, grid_usage))
    priority_bonus = load_priority * (latest_start - start_time)

    return (
        cost_vs_co2 * total_cost
        + (1.0 - cost_vs_co2) * co2_coeff * total_co2
        - prio_coeff * priority_bonus
    )


def _apply_schedule(
    load,
    grid_allocation: List[float],
    ren_allocation: List[float],
    load_grid_draw: Dict,
    load_ren_draw: Dict,
    remaining_grid: List[float],
    remaining_ren: List[float],
) -> None:
    """Apply the chosen schedule to outputs and update remaining supplies"""
    for time_idx, (grid_use, ren_use) in enumerate(
        zip(grid_allocation, ren_allocation)
    ):
        if grid_use > 0:
            load_grid_draw[load][time_idx] += grid_use
            remaining_grid[time_idx] -= grid_use
        if ren_use > 0:
            load_ren_draw[load][time_idx] += ren_use
            remaining_ren[time_idx] -= ren_use


def _clean_small_values(
    loads: List,
    load_grid_draw: Dict,
    load_ren_draw: Dict,
    remaining_ren: List[float],
) -> Tuple[Dict, Dict, List[float]]:
    """Remove numerical noise and compute renewable spill"""

    def clean_value(x):
        return 0.0 if abs(x) <= EPS else float(x)

    for load in loads:
        load_grid_draw[load] = [clean_value(x) for x in load_grid_draw[load]]
        load_ren_draw[load] = [clean_value(x) for x in load_ren_draw[load]]

    renewable_spill = [clean_value(x) for x in remaining_ren]
    return load_grid_draw, load_ren_draw, renewable_spill


def solve(params: Parameters) -> dict:
    """
    Greedy heuristic scheduler that:
    - Fixes confirmed activity windows
    - Schedules pending loads by evaluating start options greedily
    - Prioritizes renewable energy, then uses grid power
    - Optimizes for cost/CO2 trade-off with load priorities
    """
    T = len(params.times)
    loads = list(params.loads)

    # Initialize tracking structures
    load_grid_draw, load_ren_draw = _init_outputs(loads, T)
    remaining_ren = [float(x) for x in params.ren_prod]
    remaining_grid = [float(x) for x in params.grid_prod]

    # 1) Handle confirmed loads first
    confirmed_feasible = _allocate_confirmed_loads(
        loads,
        T,
        params.is_confirmed,
        params.confirmed_activity,
        params.flow_min,
        params.flow_max,
        remaining_ren,
        remaining_grid,
        load_grid_draw,
        load_ren_draw,
    )

    if not confirmed_feasible:
        return {}

    # 2) Schedule pending loads in priority order
    pending_loads = [load for load in loads if params.is_confirmed.get(load, 0) == 0]
    pending_loads.sort(key=lambda load: params.priority.get(load, 0), reverse=True)

    for load in pending_loads:
        start_options = params.start_opts.get(load, [])
        if not start_options:
            continue

        latest_start = max(start_options)
        duration = T - latest_start
        min_flow = float(params.flow_min[load])
        max_flow = float(params.flow_max[load])
        load_priority = params.priority.get(load, 0)

        best_score = None
        best_allocation = None

        # Evaluate each start option
        for start_option in start_options:
            feasible, grid_usage, ren_usage = _simulate_load_schedule(
                start_option,
                duration,
                min_flow,
                max_flow,
                remaining_ren,
                remaining_grid,
            )

            if not feasible:
                continue

            score = _calculate_schedule_score(
                start_option,
                latest_start,
                grid_usage,
                params.grid_price,
                params.grid_co2,
                params.cost_vs_co2,
                params.co2_coeff,
                params.prio_coeff,
                load_priority,
            )

            if best_score is None or score < best_score:
                best_score = score
                best_allocation = (grid_usage, ren_usage)

        # Apply the best schedule found
        if best_allocation is not None:
            grid_alloc, ren_alloc = best_allocation
            _apply_schedule(
                load,
                grid_alloc,
                ren_alloc,
                load_grid_draw,
                load_ren_draw,
                remaining_grid,
                remaining_ren,
            )

    # 3) Clean up and return results
    load_grid_draw, load_ren_draw, ren_spill = _clean_small_values(
        loads, load_grid_draw, load_ren_draw, remaining_ren
    )

    return {
        LOAD_GRID_DRAW: load_grid_draw,
        LOAD_REN_DRAW: load_ren_draw,
        REN_SPILL: ren_spill,
    }
