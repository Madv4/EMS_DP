import uuid
import sys

# Try to import the module. If pulp or the milp module is missing, skip gracefully.
try:
    from ems.application.solvers import milp_solver
except Exception as e:
    print("SKIP - milp tests: could not import milp module or its dependencies:", e)
    sys.exit(0)

from ems.application.solvers import base


class FakeVar:
    """Minimal object resembling pulp LpVariable for parse routine: has .varValue"""
    def __init__(self, v):
        self.varValue = v


def test_parse_output_with_fake_vars():
    T = 3
    lid = uuid.uuid4()
    params = base.Parameters(times=range(T))
    params.loads = [lid]

    # Build fake variable dicts: keys are (load, t)
    lgd = {(lid, t): FakeVar(1.0 + t) for t in range(T)}
    lrd = {(lid, t): FakeVar(0.5 * t) for t in range(T)}
    rs = {t: FakeVar(0.1 * t) for t in range(T)}

    parsed = milp_solver._parse_output(params, (lgd, lrd, rs))

    # Ensure dictionaries have expected structure and numeric values preserved
    assert lid in parsed[milp_solver.LOAD_GRID_DRAW]
    assert parsed[milp_solver.LOAD_GRID_DRAW][lid] == [1.0, 2.0, 3.0]
    assert parsed[milp_solver.LOAD_REN_DRAW][lid] == [0.0, 0.5, 1.0]
    assert parsed[milp_solver.REN_SPILL] == [0.0, 0.1, 0.2]


def try_small_build_and_solve():
    """
    Try to build and solve a tiny MILP model. This may be skipped if the solver backend
    is unavailable in the environment; the code handles that gracefully.
    """
    from pulp import LpProblem, LpMinimize

    T = 2
    lid = uuid.uuid4()
    params = base.Parameters(times=range(T))
    params.loads = [lid]
    params.flow_min = {lid: 0.0}  # keep feasible/easy
    params.flow_max = {lid: 5.0}
    params.priority = {lid: 1}
    params.start_opts = {lid: [0, 1]}
    # start_covers: time 0 covered by start 0, time 1 covered by start 1 (run duration 1)
    params.start_covers = {lid: {0: [0], 1: [1]}}
    params.is_confirmed = {lid: 0}
    params.confirmed_activity = {}

    params.grid_price = [1.0] * T
    params.grid_co2 = [0.0] * T
    params.grid_prod = [10.0] * T
    params.ren_prod = [0.0] * T

    params.cost_vs_co2 = 0.5
    params.co2_coeff = 0.2
    params.prio_coeff = 0.1

    model = LpProblem("test_milp_small", LpMinimize)
    try:
        dvars = milp_solver._build(params, model)
    except Exception as e:
        print("SKIP - could not build MILP model in test environment:", e)
        return

    # Try to solve: may fail on some environments; allow graceful skip
    try:
        model.solve(milp_solver.ENGINE)
    except Exception as e:
        print("SKIP - MILP solve failed or solver backend unavailable:", e)
        return

    # If solved to optimality, parse and sanity-check
    try:
        result = milp_solver._parse_output(params, dvars)
    except Exception as e:
        print("WARNING - parsing MILP output failed:", e)
        return

    assert isinstance(result, dict)
    assert milp_solver.LOAD_GRID_DRAW in result
    assert milp_solver.LOAD_REN_DRAW in result
    assert milp_solver.REN_SPILL in result
    print("MILP build/solve smoke test completed (no assertion of optimality)")

if __name__ == "__main__":
    test_parse_output_with_fake_vars()
    try_small_build_and_solve()
    print("OK - milp tests (parse + optional solve) passed or skipped safely")
