# Baseline architecture

The original repository follows a layered structure:

1. The interface layer exposes FastAPI REST routes and a WebSocket endpoint.
2. `EMSRuntime` serializes commands and advances the simulation on a timer.
3. Application services manage portfolios, advance metrics, and deploy plans.
4. The solver layer builds a schedule with MILP and uses a heuristic fallback.
5. Domain models represent portfolios, loads, plans, and time-series metrics.
6. Domain ports separate forecast and persistence abstractions from simple infrastructure adapters.

The architecture supports simulated scheduling and optimization. It contains no physical meter adapter, user or authentication subsystem, dedicated reporting service, or domain-level alert rule in the Part 1 baseline.

## Source locations

| Layer | Baseline files |
|---|---|
| Interface | `ems/interface/endpoints.py`, `runtime.py`, `server.py`, `websocket.py` |
| Application | `ems/application/services/*`, `ems/application/solvers/*` |
| Domain | `ems/domain/models/*`, `ems/domain/ports/*` |
| Infrastructure | `ems/infrastructure/simple_forecast_provider.py`, `simple_portfolio_repository.py`, `serializer.py` |

The image `architecture.png` is rendered from `architecture.mmd`.
