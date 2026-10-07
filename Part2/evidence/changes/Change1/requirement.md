# Change 1 - Dynamic tariffs

## Requirement

Allow the grid electricity price to vary according to a selectable pricing policy while preserving the existing solver contract.

Supported policies:

- Flat price for every simulation step.
- Time-of-use price with peak and off-peak periods.
- Dynamic price from an externally supplied series.

## Acceptance criteria

1. Every tariff implements a common `get_price(time_index)` operation.
2. The forecast provider converts the selected policy into the existing `GRID_PRICE` metric.
3. MILP and heuristic solvers continue to read grid prices from `Metrics` through `build_params`.
4. `PUT /tariff` selects a policy and rejects unsupported types.
5. Automated tests cover all concrete policies and provider integration.

## Pattern

Primary pattern: Strategy.
