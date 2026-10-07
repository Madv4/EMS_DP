# Part 1 pattern-to-source mapping

The submission-level collaboration records are in `data/patterns.csv`. The table below provides a readable summary. Line ranges refer to the source that will be placed under `Part1/code/`.

| Pattern | Instance | Participants | Source locations | Verification |
|---|---|---|---|---|
| Ports and Adapters | Forecast Provider Boundary | Port: `ForecastProvider`; adapter: `SimpleForecastProvider`; client: `ems_service.advance` | `ems/domain/ports/forecast_provider.py:5-20`; `ems/infrastructure/simple_forecast_provider.py:6-18`; `ems/application/services/ems_service.py:46-50` | Application code depends on the port while infrastructure supplies the implementation. |
| Ports and Adapters | Portfolio Persistence Boundary | Port: `PortfolioRepository`; adapter: `SimplePortfolioRepository`; client: `manage_portfolio.create_portfolio` | `ems/domain/ports/portfolio_repository.py:8-21`; `ems/infrastructure/simple_portfolio_repository.py:7-17`; `ems/application/services/manage_portfolio.py:9-17` | Persistence behavior is behind a domain-facing port. |
| Repository | Portfolio Repository | Repository: `PortfolioRepository`; concrete repository: `SimplePortfolioRepository`; client: portfolio service | Same repository locations above | Add, get, and delete behavior is centralized instead of implemented by the service. |
| Dependency Injection | FastAPI Runtime Injection | Provider: `get_runtime`; injected object: `EMSRuntime`; dependents: REST and WebSocket handlers | `ems/interface/runtime.py:136-138`; `ems/interface/endpoints.py:46-113`; `ems/interface/websocket.py:7-22` | `Depends(get_runtime)` supplies one shared runtime. |
| Strategy | Solver Selection | Context: `generate_plan`; concrete strategies: MILP and heuristic `solve`; separate Strategy interface: absent | `ems/application/services/deploy_plan.py:16-34`; `milp_solver.py:124-135`; `heuristic_solver.py:205-308` | The context uses compatible solver functions and a fallback path. |
| Observer | WebSocket Runtime Updates | Subject: `EMSRuntime`; observers: connected WebSocket clients; attach/detach: `websocket_endpoint`; Observer interface: absent | `ems/interface/runtime.py:11-103`; `ems/interface/websocket.py:7-22` | The runtime maintains subscribers and broadcasts snapshots after commands and timed advances. |

Roles that are combined or absent are stated explicitly. No unimplemented classes are invented.
