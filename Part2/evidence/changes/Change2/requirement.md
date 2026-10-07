# Change 2 - Renewable-energy integration

## Requirement

Extend the baseline aggregate renewable-production value into explicit renewable-source behaviors while keeping `REN_PROD` compatible with the existing planners.

Supported source types:

- Solar source with a repeatable daylight curve.
- Wind source with a supplied availability series.

## Acceptance criteria

1. Renewable sources implement a common energy-availability operation.
2. A factory creates concrete source objects from configuration.
3. The provider retains per-source production and aggregates it into `REN_PROD`.
4. Existing solvers consume the aggregate without modification.
5. REST and WebSocket output expose configured sources and latest production.
6. Tests verify production behavior, aggregation, validation, and API configuration.

## Patterns

Primary pattern: Strategy. Supporting pattern: Factory.
