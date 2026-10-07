# Baseline source-code excerpts

The excerpts below identify the evidence used in Part 1. Add the original application to `Part1/code/` before final submission so every path resolves inside the repository.

## Energy consumption and renewable metrics

From `ems/domain/models/types.py`:

```python
GRID_PRICE = "grid_price"
REN_PROD = "ren_prod"
LOAD_GRID_DRAW = "load_grid_draw"
LOAD_REN_DRAW = "load_ren_draw"
REN_SPILL = "ren_spill"
```

These keys show explicit grid consumption, renewable consumption, renewable production, and spill.

## Forecast-provider port

From `ems/domain/ports/forecast_provider.py`:

```python
class ForecastProvider(ABC):
    @abstractmethod
    def get_forecast_entry(self) -> dict[MetricKey, float]:
        pass
```

The infrastructure adapter implements the port and supplies simulated forecast values.

## Solver selection

From `ems/application/services/deploy_plan.py`:

```python
updates = primary.solve(params)
if not updates:
    updates = fallback.solve(params)
```

The planning service attempts MILP first and invokes a compatible heuristic fallback.

## Runtime subscribers

From `ems/interface/runtime.py`:

```python
self.subscribers: List[Any] = []

for ws in subscribers:
    await ws.send_json(snapshot)
```

This is live state publication. The Part 1 baseline has no business rule that converts consumption into an alert.
