# B13 - Design Pattern Identification and Evolution in a FastAPI Energy Management Application

This folder contains Team B13's completed 23CSE455 Design Pattern Case Study: baseline pattern discovery, three FastAPI evolution scenarios, and a four-language comparison of Strategy and Observer.

## Team B13

| Roll number | Name | Programme / batch |
|---|---|---|
| AM.SC.U4CSE23306 | Anand Narayan | S7 CSE D |
| AM.SC.U4CSE23346 | S H Saimadhav | S7 CSE D |
| AM.SC.U4CSE23365 | Vaishnav P Nair | S7 CSE D |
| AM.SC.U4CSE23369 | Vishnu M | S7 CSE D |

## Application and source record

- Application: FastAPI Energy Management System for simulated load scheduling and optimization.
- Local application URL after startup: `http://localhost:8000`; Swagger UI: `http://localhost:8000/docs`.
- Original source: supplied archive `energy-management-system-main.zip`. An upstream source URL was not present in the supplied archive.
- Original source SHA-256: `A53D974449C1CCC0BA322267DB37BD7CDD626CC8E80C55C604EBEBF757FCC060`.
- Evolved source: `energy-management-system-part2.zip` produced for this case study.
- Evolved source SHA-256: `19A9AAF2447540E38AB6E1667B664E64B535E36B2E8B23580181DF1A1725FD8C`.
- Git commits: unavailable because the supplied source archive contained no Git history. The archive hashes above identify the inspected versions.
- Submission repository: `https://github.com/aswathymohan-amrita/23CSE455_DP_CaseStudy`, team folder `B13/`.

## Current completion state

| Area | Status | Evidence |
|---|---|---|
| Part 1 - Pattern Discovery | Complete | Seven-area investigation, architecture, confirmed pattern collaborations, exact source mappings, UML, and LLM record |
| Part 2 - Software Evolution | Complete | Dynamic tariffs, renewable-source integration, consumption alerts, diffs, before/after analysis, tests, updated UML, and LLM record |
| Part 3 - Cross-Language Analysis | Complete with stated measurement limits | Strategy and Observer implementations cover four languages; test evidence, static metrics, cross-language analysis, and Python/JavaScript timings are recorded |
| Report | Final content prepared | `B13_Report.tex` follows the prescribed report format and references the architecture, UML, Swagger, terminal, and cross-language evidence images. Add the final GitHub folder-tree screenshot and compile the submission PDF in Overleaf. |
| Slides | Complete | Ten-slide deck covers Parts 1-3, Part 2 verification, the Part 3 language matrix, and measured timing results. |

## Submission artifacts

- `B13_Report.tex`: editable report source in the prescribed format.
- `B13_Report.pdf`: compiled report; regenerate this from the latest TeX source after adding the final folder-tree screenshot.
- `B13_Slides.pptx`: editable presentation covering Parts 1-3.
- `B13_slide.pdf`: PDF export of the presentation.
- `.gitignore`: excludes virtual environments, caches, compiled binaries, dependency folders, LaTeX auxiliary files, and IDE metadata.
- `data/`: consolidated pattern, evolution, cross-language, and LLM datasets.

## Dataset files

The submission keeps one dataset folder and does not duplicate these CSVs inside the Part folders.

- `data/patterns.csv`: one confirmed original-code collaboration per row.
- `data/pattern_counts.csv`: per-pattern and total counts for each source version.
- `data/patterns_evolution.csv`: continuing and newly introduced collaborations after Changes 1-3.
- `data/cross_language.csv`: eight language-pattern records with LOC, complexity, commands, results, measured timings where available, and language notes.
- `data/llm.csv`: AI interactions and human verification evidence.

All paths inside CSV cells are relative to this `B13/` folder. CSV files use UTF-8, one header row, and the column names required by `DP_Csestudy.pdf`.

## Code folders requiring manual upload

- `Part1/code/`: add the original application source from `energy-management-system-main.zip`.
- `Part2/code/`: add the evolved application source from `energy-management-system-part2.zip`.
- `Part3/code/`: add the sixteen verified production and test-runner files supplied separately.

These directories are intentionally empty in this package, as requested.

## Evidence images used by the report

The Overleaf report references these filenames:

- Baseline: `architecture.png`, `pattern_uml.png`.
- Dynamic tariffs: `put_tariff1.png`, `put_tariff2.png`, `put_tariff3.png`, `put_tariff_terminal.png`.
- Renewable integration: `renewable_class_diagram.png`, `Swagger_post_energy_sources.png`, `swagger_get_energy_sources.png`.
- Consumption alerts: `alert_sequence_diagram.png`, `put_alerts.png`, `get_alerts.png`, `13_passed.png`.
- Part 3 Strategy runs: `dynamic_tariff_java.png`, `dynamic_tariff_python.png`, `dynamic_tariff_javascript.png`, `dynamic_tariff_cpp.png`.
- Part 3 Observer runs: `consumption_alert_java.png`, `consumption_alert_python.png`, `consumption_alert_javascript.png`, `consumption_alert_cpp.png`.

For the GitHub evidence package, retain the diagrams in their existing evidence directories. Store Part 2 Swagger and terminal captures in the appropriate `Part2/evidence/changes/ChangeN/screenshots/` directory. Store the eight Part 3 terminal captures under `Part3/evidence/test_results/screenshots/`. The report may use shorter Overleaf paths because its uploaded image files are colocated with the TeX project.

## Inspected modules

- `ems/domain/models/`: portfolios, loads, plans, metrics, and metric types.
- `ems/domain/ports/`: forecast, repository, and evolved energy-configuration abstractions.
- `ems/application/services/`: metric advancement, planning, portfolio management, energy configuration, and event publication.
- `ems/application/solvers/`: MILP and heuristic scheduling algorithms.
- `ems/infrastructure/`: forecast and repository adapters plus serialization.
- `ems/interface/`: REST routes, runtime orchestration, server lifecycle, and WebSocket delivery.
- `test/`: baseline solver checks and Part 2 evolution tests.

## Verified environment

| Component | Version / value |
|---|---|
| Operating system | Windows |
| Python | 3.12.14 |
| FastAPI | 0.142.2 |
| Pydantic | 2.13.5 |
| pytest | 9.1.1 |
| PuLP | 3.3.2 |
| httpx | 0.28.1 |

## Run and test commands

After adding the evolved source to `Part2/code/`:

```powershell
cd Part2/code
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest -q test
python -m test.test_milp_solver
python -m ems
```

Verified Part 2 result: `13 passed in 0.53s`. The MILP build-and-solve smoke test also completed. Open Swagger UI at `http://localhost:8000/docs` after starting the application.

## Part 3 execution

Each pattern problem uses the same conceptual cases in Java, Python, JavaScript, and C++. Run the commands from the corresponding language directory after adding the supplied source files to `Part3/code/`.

| Pattern | Language | Command |
|---|---|---|
| Dynamic Tariff Strategy | Java | `javac StrategyTariff.java StrategyTariffTest.java && java StrategyTariffTest` |
| Dynamic Tariff Strategy | Python | `python test_strategy_tariff.py` |
| Dynamic Tariff Strategy | JavaScript | `node strategyTariff.test.js` |
| Dynamic Tariff Strategy | C++ | `g++ -std=c++17 -O2 -Wall -Wextra -pedantic test_strategy_tariff.cpp -o test_strategy_tariff` followed by the generated executable |
| Consumption Alert Observer | Java | `javac ConsumptionAlert.java ConsumptionAlertTest.java && java ConsumptionAlertTest` |
| Consumption Alert Observer | Python | `python test_consumption_alert.py` |
| Consumption Alert Observer | JavaScript | `node consumptionAlert.test.js` |
| Consumption Alert Observer | C++ | `g++ -std=c++17 -O2 -Wall -Wextra -pedantic test_consumption_alert.cpp -o test_consumption_alert` followed by the generated executable |

Expected results are 17/17 for each Strategy implementation and 10/10 for each Observer implementation. Detailed commands, versions, results, and available timings are recorded in `data/cross_language.csv`.

## Measurement rules

- Source LOC for Part 3: count production-code lines only; exclude blank lines, comments, and test files.
- Cyclomatic complexity: record the maximum function complexity using one named tool and the same decision-counting rule across languages.
- Timing: compile first, perform one warmup, then five measured process runs on the same machine and report the median in milliseconds.
- Timing scope: process startup, test-input reading, pattern execution, and result validation are included unless a language README explicitly records a narrower consistent scope.
- Never estimate an unavailable result. Use `not_run` with a reason and leave `median_process_ms` blank.

## Limitations

- The application uses simulated forecast and consumption data; it does not ingest physical smart-meter telemetry.
- It has no user, authentication, authorization, or role-management domain.
- Part 2 alert records are in memory and exposed through REST and WebSocket; email and SMS delivery were not implemented.
- Solar and wind models are deterministic simulation strategies rather than physical forecasting models.
- Java and C++ test passes are user-confirmed because raw terminal output and toolchain versions were not supplied to this workspace.
- Java and C++ execution-time fields remain blank because the required five measured runs were not supplied; no timing was estimated.