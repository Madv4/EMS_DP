from dataclasses import dataclass, field
import uuid

from ems.domain.models.portfolio import Portfolio
from ems.domain.models.metrics import Metrics
from ems.domain.models.types import LoadStatus, MetricKey

LOAD_GRID_DRAW = MetricKey.LOAD_GRID_DRAW
LOAD_REN_DRAW = MetricKey.LOAD_REN_DRAW
REN_SPILL = MetricKey.REN_SPILL


@dataclass(slots=True)
class Parameters:
    """Container for solver parameters"""

    loads: list[uuid.UUID] = field(default_factory=list)
    times: range = range(24)

    flow_min: dict[uuid.UUID, float] = field(default_factory=dict)
    flow_max: dict[uuid.UUID, float] = field(default_factory=dict)
    priority: dict[uuid.UUID, int] = field(default_factory=dict)
    start_opts: dict[uuid.UUID, list[int]] = field(default_factory=dict)
    start_covers: dict[uuid.UUID, dict[int, list[int]]] = field(default_factory=dict)

    is_confirmed: dict[uuid.UUID, int] = field(default_factory=dict)
    confirmed_activity: dict[uuid.UUID, list[int]] = field(default_factory=dict)

    grid_price: list[float] = field(default_factory=list)
    grid_co2: list[float] = field(default_factory=list)
    grid_prod: list[float] = field(default_factory=list)
    ren_prod: list[float] = field(default_factory=list)

    cost_vs_co2: float = 0.5
    co2_coeff: float = 0.2
    prio_coeff: float = 0.1


def build_params(portfolio: Portfolio, metrics: Metrics) -> Parameters:
    """Builds Parameters from a Portfolio and forward Metrics, with basic validation

    Validation performed:
      - metrics.is_forward is True
      - each load.run_duration <= metrics.duration
      - lengths of all time series == metrics.duration
      - consistent dict keys across load-keyed fields
      - confirmed_activity keys ⊆ loads keys
      - is_confirmed, confirmed_activity are binary
      - 0 <= flow_min[l] <= flow_max[l] for all loads
      - grid_prod[t], ren_prod[t] >= 0
    """

    if not metrics.is_forward:
        raise ValueError("ParamsBuilder expects forward-facing (forecast) metrics")
    if not portfolio.get_active_loads():
        raise ValueError("no active loads to plan")

    T = metrics.duration
    params = Parameters(times=range(T))

    # Per-load attributes
    for load in portfolio.loads.values():
        if load.status == LoadStatus.OFF:
            continue  # skip entirely

        # Enforce run duration vs horizon
        if load.run_duration > T:
            raise ValueError("Load run duration exceeds metrics duration")

        l_id = load.load_id
        params.loads.append(l_id)
        params.flow_min[l_id] = load.throughput[0]
        params.flow_max[l_id] = load.throughput[1]
        params.priority[l_id] = load.priority

        # Start options and coverage windows
        last_start = T - load.run_duration
        start_opts = list(range(last_start + 1))
        params.start_opts[l_id] = start_opts
        params.start_covers[l_id] = {
            t: [so for so in start_opts if so <= t < so + load.run_duration]
            for t in params.times
        }

        # Confirmation flags and activity
        if load.status in {LoadStatus.CONFIRMED, LoadStatus.RUNNING}:
            params.is_confirmed[l_id] = 1

            # Derive activity from forward schedule metrics (LGD + LRD)
            lgd = metrics.get_load_metric(LOAD_GRID_DRAW, l_id)
            lrd = metrics.get_load_metric(LOAD_REN_DRAW, l_id)
            if len(lgd) != T or len(lrd) != T:
                raise ValueError("Schedule metric length does not conform to duration")

            activity = [1 if (g + r) > 0.0 else 0 for g, r in zip(lgd, lrd)]
            params.confirmed_activity[l_id] = activity
        else:
            params.is_confirmed[l_id] = 0

    # Source series
    params.grid_price = metrics.get_source_metric(MetricKey.GRID_PRICE)
    params.grid_co2 = metrics.get_source_metric(MetricKey.GRID_CO2)
    params.grid_prod = metrics.get_source_metric(MetricKey.GRID_PROD)
    params.ren_prod = metrics.get_source_metric(MetricKey.REN_PROD)

    # Scalar weights
    params.cost_vs_co2 = portfolio.cost_vs_emission_weight
    params.co2_coeff = portfolio.emission_coeff
    params.prio_coeff = portfolio.priority_coeff

    _validate(params)
    return params


def _validate(params: Parameters) -> None:
    T = params.times.stop  # since times is range(0, T)

    # Time series lengths
    series = [
        params.grid_price,
        params.grid_co2,
        params.grid_prod,
        params.ren_prod,
    ] + list(params.confirmed_activity.values())
    if any(len(s) != T for s in series):
        raise ValueError("Metric list length does not conform to times.stop")

    # Non-negative capacities
    if any(x < 0 for x in params.grid_prod) or any(x < 0 for x in params.ren_prod):
        raise ValueError("grid_prod and ren_prod must be non-negative")

    # flow_min <= flow_max
    for l in params.loads:
        fmin = params.flow_min.get(l)
        fmax = params.flow_max.get(l)
        if fmin is None or fmax is None or fmin > fmax:
            raise ValueError("flow_min must be <= flow_max for all loads")

    # Consistent load-keyed dicts
    L = set(params.loads)
    keyed = [
        params.flow_min,
        params.flow_max,
        params.priority,
        params.start_opts,
        params.start_covers,
        params.is_confirmed,
    ]
    if any(set(d.keys()) != L for d in keyed):
        raise ValueError("Load-keyed dicts must share the same keys as loads")
    if not set(params.confirmed_activity.keys()).issubset(L):
        raise ValueError("confirmed_activity keys must be a subset of loads")

    # Binary checks
    if not set(params.is_confirmed.values()).issubset({0, 1}):
        raise ValueError("is_confirmed must be binary")
    for act in params.confirmed_activity.values():
        if not set(act).issubset({0, 1}):
            raise ValueError("confirmed_activity vectors must be binary")
