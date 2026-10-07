# Dynamic tariff source mapping

| Responsibility | Evolved source |
|---|---|
| Strategy interface | `ems/domain/tariff/tariff_strategy.py` |
| Flat pricing | `ems/domain/tariff/flat_tariff.py` |
| Time-of-use pricing | `ems/domain/tariff/time_of_use_tariff.py` |
| Supplied price series | `ems/domain/tariff/dynamic_tariff.py` |
| Policy selection service | `ems/application/services/manage_energy.py` |
| Forecast integration | `ems/infrastructure/simple_forecast_provider.py` |
| FastAPI request and route | `ems/interface/endpoints.py` |
| Tests | `test/test_part2_evolution.py::test_tariff_strategies_and_provider_integration` |

The solver boundary remains at `ems/application/solvers/base.py`, which reads `MetricKey.GRID_PRICE` from forward metrics.
