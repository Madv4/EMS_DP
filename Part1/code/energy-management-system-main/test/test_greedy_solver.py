import uuid

from ems.application.solvers import heuristic_solver
from ems.application.solvers import base


def test_allocate_energy_to_load():
    ren, grid, feasible = heuristic_solver._allocate_energy_to_load(5.0, available_ren=2.0, available_grid=3.0)
    assert abs(ren - 2.0) < 1e-12
    assert abs(grid - 3.0) < 1e-12
    assert feasible

    # not enough total energy
    ren2, grid2, feasible2 = heuristic_solver._allocate_energy_to_load(5.0, available_ren=1.0, available_grid=3.0)
    assert feasible2 is False


def test_simulate_and_solve_confirmed():
    T = 3
    lid = uuid.uuid4()
    params = base.Parameters(times=range(T))
    params.loads = [lid]
    params.flow_min = {lid: 2.0}
    params.flow_max = {lid: 3.5}
    params.priority = {lid: 1}
    params.start_opts = {lid: [0]}
    params.start_covers = {lid: {t: [0] for t in range(T)}}
    params.is_confirmed = {lid: 1}
    params.confirmed_activity = {lid: [1, 1, 0]}

    # available supplies
    params.ren_prod = [2.0, 1.0, 0.0]
    params.grid_prod = [1.0, 2.0, 0.0]

    # trivial source metadata (used in scoring only)
    params.grid_price = [0.5] * T
    params.grid_co2 = [0.2] * T
    params.cost_vs_co2 = 0.5
    params.co2_coeff = 0.2
    params.prio_coeff = 0.1

    out = heuristic_solver.solve(params)
    assert out, "expected non-empty result for feasible confirmed loads"

    lgd = out[heuristic_solver.LOAD_GRID_DRAW][lid]
    lrd = out[heuristic_solver.LOAD_REN_DRAW][lid]

    # Expected: t0 uses renewable 2.0 (min satisfied), grid 0.0
    assert lrd[0] >= 1.9999999999
    assert lgd[0] == 0.0

    # t1 had ren 1.0 (used) and grid may top-up to meet min 2.0
    assert lrd[1] >= 0.9999999999
    assert lgd[1] >= 0.0

    # t2 is inactive
    assert lrd[2] == 0.0 and lgd[2] == 0.0


def test_solve_infeasible_confirmed_returns_empty():
    # Confirmed load with min requirements that cannot be met -> expect {}
    T = 2
    lid = uuid.uuid4()
    params = base.Parameters(times=range(T))
    params.loads = [lid]
    params.flow_min = {lid: 5.0}
    params.flow_max = {lid: 5.0}
    params.priority = {lid: 1}
    params.start_opts = {lid: [0]}
    params.start_covers = {lid: {t: [0] for t in range(T)}}
    params.is_confirmed = {lid: 1}
    params.confirmed_activity = {lid: [1, 1]}
    params.ren_prod = [1.0, 1.0]
    params.grid_prod = [1.0, 1.0]  # insufficient to cover required min
    params.grid_price = [1.0] * T
    params.grid_co2 = [1.0] * T

    out = heuristic_solver.solve(params)
    assert out == {}, f"Expected empty dict for infeasible confirmed loads, got {out}"


def test_clean_small_values():
    lid = uuid.uuid4()
    loads = [lid]
    load_grid_draw = {lid: [1e-13, -1e-13, 0.5]}
    load_ren_draw = {lid: [0.0, 1e-13, 2e-13]}
    remaining_ren = [1e-13, 0.0, 3e-13]

    lgd, lrd, spill = heuristic_solver._clean_small_values(loads, load_grid_draw, load_ren_draw, remaining_ren)

    # small noise -> zeroed
    assert lgd[lid][0] == 0.0 and lgd[lid][1] == 0.0 and abs(lgd[lid][2] - 0.5) < 1e-12
    assert lrd[lid][0] == 0.0 and lrd[lid][1] == 0.0
    assert spill[0] == 0.0 and spill[2] == 0.0


if __name__ == "__main__":
    test_allocate_energy_to_load()
    test_simulate_and_solve_confirmed()
    test_solve_infeasible_confirmed_returns_empty()
    test_clean_small_values()
    print("OK - greedy solver tests passed")
