# Renewable integration - before and after

## Before

The baseline already modeled renewable energy through `REN_PROD`, `LOAD_REN_DRAW`, and `REN_SPILL`. `SimpleForecastProvider` supplied one random aggregate value. The system could not distinguish solar, wind, or another source.

```text
One mock renewable value
        -> REN_PROD
        -> solver allocation and spill
```

## After

`RenewableSource` defines `get_available_energy(time_index)`. `SolarSource` and `WindSource` provide different production behaviors. `EnergySourceFactory` creates a source from the API configuration. The provider stores the per-source output and sums it into the existing `REN_PROD` metric.

```text
SolarSource + WindSource
        -> per-source production
        -> aggregate REN_PROD
        -> unchanged solver allocation and spill
```

## Refactoring effect

- Individual source behavior becomes explicit and independently testable.
- Configuration code does not construct concrete classes throughout the application.
- The solver continues to receive one renewable-production series.
- `GET /energy-sources` and WebSocket snapshots expose the source breakdown.

## Simulation decision

Solar capacity follows a sine-shaped daylight profile from 06:00 through 18:00. Wind capacity multiplies a repeatable list of availability fractions between 0 and 1.
