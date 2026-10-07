import uuid

# Import the module under test
from ems.application.solvers import base
from ems.domain.models.types import LoadStatus, MetricKey


def _make_fake_load(lid, status, run_duration, throughput, priority):
    class Load:
        def __init__(self, load_id, status, run_duration, throughput, priority):
            self.load_id = load_id
            self.status = status
            self.run_duration = run_duration
            self.throughput = throughput
            self.priority = priority

    return Load(lid, status, run_duration, throughput, priority)


class FakePortfolio:
    def __init__(self, loads):
        # loads: list of objects with attributes used by build_params
        self.loads = {l.load_id: l for l in loads}
        # weights used by builder
        self.cost_vs_emission_weight = 0.6
        self.emission_coeff = 0.3
        self.priority_coeff = 0.2

    def get_active_loads(self):
        # truthy if there are loads not OFF
        return [l for l in self.loads.values() if l.status != LoadStatus.OFF]


class FakeMetrics:
    def __init__(self, duration, is_forward=True):
        self.duration = duration
        self.is_forward = is_forward
        self._source = {}
        self._load = {}

    def set_source(self, key, series):
        self._source[key] = series

    def set_load(self, key, load_id, series):
        self._load[(key, load_id)] = series

    def get_source_metric(self, key):
        return self._source.get(key, [])

    def get_load_metric(self, key, load_id):
        return self._load.get((key, load_id), [])


def test_build_params_success():
    T = 4
    lid = uuid.uuid4()
    load = _make_fake_load(lid, LoadStatus.CONFIRMED, run_duration=2, throughput=(1.0, 3.0), priority=5)
    portfolio = FakePortfolio([load])

    metrics = FakeMetrics(T, is_forward=True)
    # source series
    for k in (MetricKey.GRID_PRICE, MetricKey.GRID_CO2, MetricKey.GRID_PROD, MetricKey.REN_PROD):
        metrics.set_source(k, [0.5] * T)

    # per-load schedule metrics (length T)
    lgd = [0.0, 1.0, 0.0, 0.0]
    lrd = [0.0, 0.0, 1.0, 0.0]
    metrics.set_load(MetricKey.LOAD_GRID_DRAW, lid, lgd)
    metrics.set_load(MetricKey.LOAD_REN_DRAW, lid, lrd)

    params = base.build_params(portfolio, metrics)

    assert lid in params.loads
    assert params.flow_min[lid] == 1.0
    assert params.flow_max[lid] == 3.0
    assert params.is_confirmed[lid] == 1
    expected_activity = [1 if (g + r) > 0.0 else 0 for g, r in zip(lgd, lrd)]
    assert params.confirmed_activity[lid] == expected_activity
    assert len(params.grid_price) == T


def test_build_params_invalid_length_raises():
    T = 3
    lid = uuid.uuid4()
    load = _make_fake_load(lid, LoadStatus.CONFIRMED, run_duration=1, throughput=(1.0, 2.0), priority=1)
    portfolio = FakePortfolio([load])
    metrics = FakeMetrics(T, is_forward=True)

    # intentionally make one source series the wrong length to trigger validation
    metrics.set_source(MetricKey.GRID_PRICE, [1.0] * (T - 1))  # wrong length
    metrics.set_source(MetricKey.GRID_CO2, [0.0] * T)
    metrics.set_source(MetricKey.GRID_PROD, [0.0] * T)
    metrics.set_source(MetricKey.REN_PROD, [0.0] * T)
    metrics.set_load(MetricKey.LOAD_GRID_DRAW, lid, [0.0] * T)
    metrics.set_load(MetricKey.LOAD_REN_DRAW, lid, [0.0] * T)

    try:
        base.build_params(portfolio, metrics)
        assert False, "Expected ValueError due to source series length mismatch"
    except ValueError as e:
        # error message may vary but must indicate a length/validation problem
        assert "does not conform" in str(e) or "length" in str(e)


if __name__ == "__main__":
    test_build_params_success()
    test_build_params_invalid_length_raises()
    print("OK - base params tests passed")
