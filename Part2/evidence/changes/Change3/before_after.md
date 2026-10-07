# Consumption alerts - before and after

## Before

Backward `Metrics` stored actual load draw and `EMSRuntime` broadcast the context. The baseline had no rule deciding when consumption represented an alert.

```text
Actual grid and renewable draw
        -> backward Metrics
        -> generic WebSocket snapshot
```

## After

`ems_service.advance` calculates each load's completed-step consumption after both draw metrics have moved to backward metrics. `ConsumptionSubject` publishes one `ConsumptionEvent`. `ConsumptionAlertObserver` records entries above its configured threshold.

```text
Actual grid + renewable draw
        -> ConsumptionEvent
        -> ConsumptionSubject
        -> subscribed threshold observer
        -> REST and WebSocket alert output
```

## Refactoring effect

- The EMS publishes a domain event without evaluating every alert rule itself.
- Additional observers can subscribe to the same event.
- Threshold configuration and alert querying are application services.
- The baseline portfolio, metric, and solver APIs remain available.

## Rule semantics

The default threshold is 10.0 simulation energy units per load per completed step. An alert occurs when consumption is strictly greater than the threshold. The implementation records alerts in memory and does not send email or SMS.
