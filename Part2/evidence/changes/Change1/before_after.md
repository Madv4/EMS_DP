# Dynamic tariffs - before and after

## Before

`SimpleForecastProvider` generated a deterministic random value between 0.1 and 0.3 for every new `GRID_PRICE` entry. The solvers correctly consumed the price series, but the application could not express a flat tariff, peak period, or supplied market-price series as a named behavior.

```text
SimpleForecastProvider random value
        -> GRID_PRICE
        -> Metrics
        -> build_params
        -> MILP or heuristic solver
```

## After

`TariffStrategy` defines `get_price(time_index)`. `FlatTariff`, `TimeOfUseTariff`, and `DynamicTariff` implement the operation. `SimpleForecastProvider` uses the selected strategy and writes the result into the unchanged `GRID_PRICE` metric.

```text
Selected TariffStrategy
        -> GRID_PRICE
        -> Metrics
        -> build_params
        -> unchanged solvers
```

## Refactoring effect

- Tariff decisions are outside both solvers.
- New price policies can implement the same interface.
- Existing scheduling code remains compatible.
- The provider retains the original deterministic random behavior when no tariff is selected.

## Simulation decision

One simulation step represents one hour for time-of-use behavior. A dynamic price series repeats after its final entry so a short demonstration series can support a continuously running simulation.
