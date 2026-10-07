# B13 - Design Pattern Identification and Evolution in a FastAPI Energy Management Application

This folder is the B13 submission workspace for the 23CSE455 Design Pattern Case Study. It contains the completed Part 1 baseline analysis, Part 2 evolution evidence, and Part 3 cross-language comparison.

## Team B13

| Roll number | Name | Programme / batch |
|---|---|---|
| AM.SC.U4CSE23306 | Anand Narayan | CSE 2023 |
| AM.SC.U4CSE23346 | S H Saimadhav | CSE 2023 |
| AM.SC.U4CSE23365 | Vaishnav P Nair | CSE 2023 |
| AM.SC.U4CSE23369 | Vishnu M | CSE 2023 |

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
| Report and slides | Updated | Covers Parts 1-3 and distinguishes tool-captured results from user-confirmed Java/C++ results |

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

## Final submission checklist

- Add the original source under `Part1/code/` and evolved source under `Part2/code/`.
- Add the sixteen Part 3 production and test-runner files under `Part3/code/`.
- Add Java and C++ terminal captures and five-run timing values if they are available before submission.
- Recheck all team-relative paths after adding the three code versions.
