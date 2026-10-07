# Part 3 - Cross-Language Analysis

## Status

The source implementations and test runners are complete for both selected patterns in Java, Python, JavaScript, and C++. The `code/` directory is intentionally empty in this package so the team can add its verified source files separately.

## Selected pattern problems

1. **Strategy - Dynamic Tariff Selection**
   - Common abstraction: tariff strategy.
   - Concrete behaviors: flat, time-of-use, and repeating dynamic price series.
   - Context: selects a strategy and requests a price for a time index.
   - Shared functional cases: `test_cases/dynamic_tariff.csv` (`DT01`-`DT10`).
   - Test runners also check invalid prices, invalid peak windows, empty series, and negative indices.

2. **Observer - Consumption Threshold Alerts**
   - Subject: manages subscriptions and publishes consumption events.
   - Observer abstraction: receives one event at a time.
   - Concrete observer: records loads whose consumption is strictly greater than a positive threshold.
   - Shared functional cases: `test_cases/consumption_alert.csv` (`CA01`-`CA05`).
   - Test runners also check duplicate subscription, unsubscribe behavior, multiple loads, and invalid thresholds.

## Expected code files

Add these files manually under `Part3/code/`:

```text
strategy_tariff/
  java/StrategyTariff.java
  java/StrategyTariffTest.java
  python/strategy_tariff.py
  python/test_strategy_tariff.py
  javascript/strategyTariff.js
  javascript/strategyTariff.test.js
  cpp/strategy_tariff.hpp
  cpp/test_strategy_tariff.cpp

observer_consumption_alert/
  java/ConsumptionAlert.java
  java/ConsumptionAlertTest.java
  python/consumption_alert.py
  python/test_consumption_alert.py
  javascript/consumptionAlert.js
  javascript/consumptionAlert.test.js
  cpp/consumption_alert.hpp
  cpp/test_consumption_alert.cpp
```

## Test commands

Run each command from its language directory.

| Pattern | Language | Command | Expected result |
|---|---|---|---|
| Strategy | Java | `javac StrategyTariff.java StrategyTariffTest.java; java StrategyTariffTest` | `Strategy tests: 17/17 passed` |
| Strategy | Python | `python test_strategy_tariff.py` | `Strategy tests: 17/17 passed` |
| Strategy | JavaScript | `node strategyTariff.test.js` | `Strategy tests: 17/17 passed` |
| Strategy | C++ | `g++ -std=c++17 -O2 -Wall -Wextra -pedantic test_strategy_tariff.cpp -o test_strategy_tariff; ./test_strategy_tariff` | `Strategy tests: 17/17 passed` |
| Observer | Java | `javac ConsumptionAlert.java ConsumptionAlertTest.java; java ConsumptionAlertTest` | `Observer tests: 10/10 passed` |
| Observer | Python | `python test_consumption_alert.py` | `Observer tests: 10/10 passed` |
| Observer | JavaScript | `node consumptionAlert.test.js` | `Observer tests: 10/10 passed` |
| Observer | C++ | `g++ -std=c++17 -O2 -Wall -Wextra -pedantic test_consumption_alert.cpp -o test_consumption_alert; ./test_consumption_alert` | `Observer tests: 10/10 passed` |

## Verified results

- Python 3.12.14: both runners passed in this workspace.
- Node.js 24.21.0: both runners passed in this workspace.
- Java: both runners passed according to the team's human verification; the JDK version and raw terminal output were not supplied to this workspace.
- C++17: both runners passed according to the team's human verification; the compiler version and raw terminal output were not supplied to this workspace.

Detailed records are under `evidence/test_results/`.

## Measurement rules

- **Source LOC:** production file only; blank lines, comment-only lines, and test files are excluded.
- **Cyclomatic complexity:** manual McCabe count per production function or method. Begin at 1 and add 1 for each `if`, loop, `case`, catch/except handler, conditional expression, and short-circuit Boolean operator. `max_function_cc` is the largest function value in that production file.
- **Timing:** compile first where applicable; perform one unrecorded warmup and then five measured process runs on the same machine; report the median.
- **Timing scope:** process startup, test-runner loading, all assertions, and output are included. Compilation is excluded.
- Missing measurements are left blank. They are never estimated.

## Limitations

- Python and JavaScript timings were measured in this workspace. They compare complete runner processes rather than isolated pattern method calls.
- Java and C++ execution times remain blank because raw five-run measurements and toolchain versions were not supplied.
- Process timings depend on hardware, operating-system scheduling, runtime startup, and background activity. They should not be interpreted as general language benchmarks.
