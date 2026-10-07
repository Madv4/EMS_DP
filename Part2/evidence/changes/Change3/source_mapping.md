# Consumption alert source mapping

| Responsibility | Evolved source |
|---|---|
| Event and observer interface | `ems/domain/alerts/observer.py` |
| Subscription and notification | `ems/domain/alerts/alert_subject.py` |
| Threshold rule and alert record | `ems/domain/alerts/consumption_alert.py` |
| Observer ownership and event emission | `ems/application/services/ems_service.py` |
| Threshold and query services | `ems/application/services/manage_energy.py` |
| REST routes | `ems/interface/endpoints.py` |
| WebSocket snapshot | `ems/interface/runtime.py` |
| Tests | `test/test_part2_evolution.py::test_observer_subscription_and_threshold` and `test_actual_consumption_emits_one_alert_after_both_draws` |
