# Renewable source mapping

| Responsibility | Evolved source |
|---|---|
| Source strategy interface | `ems/domain/energy_sources/source.py` |
| Solar behavior | `ems/domain/energy_sources/solar.py` |
| Wind behavior | `ems/domain/energy_sources/wind.py` |
| Source construction | `ems/domain/energy_sources/factory.py` |
| Optional provider capability port | `ems/domain/ports/energy_configuration.py` |
| Aggregation and latest breakdown | `ems/infrastructure/simple_forecast_provider.py` |
| Configuration services | `ems/application/services/manage_energy.py` |
| REST routes | `ems/interface/endpoints.py` |
| WebSocket snapshot | `ems/interface/runtime.py` |
| Tests | `test/test_part2_evolution.py::test_renewable_sources_aggregate_into_existing_metric` |

`ems/application/solvers/base.py` still maps `MetricKey.REN_PROD` to `Parameters.ren_prod`, preserving both solver implementations.
