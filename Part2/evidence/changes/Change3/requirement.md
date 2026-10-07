# Change 3 - Consumption alerts

## Requirement

Detect excessive actual per-load consumption and expose generated alerts without coupling the EMS engine to a specific alert rule or delivery channel.

## Acceptance criteria

1. The EMS publishes one consumption event after a completed simulation step.
2. Consumption combines the recorded grid and renewable draw for each load.
3. Observers can subscribe and unsubscribe.
4. The threshold observer records an alert only when consumption is greater than the threshold.
5. The threshold can be changed through REST.
6. Alerts appear through REST and WebSocket snapshots.
7. Tests cover below-threshold behavior, above-threshold behavior, observer removal, service integration, and API exposure.

## Pattern

Primary pattern: Observer.
