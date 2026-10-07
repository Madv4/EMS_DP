# Energy Management System (EMS)

A modular, extensible Energy Management System (EMS) for scheduling and optimizing energy loads in a simulated environment. This project provides a FastAPI-based backend for managing energy portfolios, forecasting, and real-time scheduling using both MILP and heuristic solvers.

---

## Features

- **Portfolio Management**: Create, open, patch, and delete energy portfolios, each containing configurable loads.
- **Load Scheduling**: Add, modify, and remove loads with customizable throughput, priority, and run durations.
- **Forecast Integration**: Pluggable forecast providers for energy price, CO₂, and production forecasts.
- **Optimization Solvers**: MILP (via PuLP) and greedy heuristic solvers for load scheduling and energy allocation.
- **Simulation & Metrics**: Stepwise simulation of energy flows, with forward (forecasted/planned) and backward (actual) metrics.
- **WebSocket Streaming**: Real-time updates of EMS context to connected clients.
- **Extensible Architecture**: Clean separation of domain, application, infrastructure, and interface layers.

---

## Project Structure

```
ems/
    __main__.py                  # Entry point for running the FastAPI server
    application/
        services/                # Core business logic (advance, deploy, manage portfolio)
        solvers/                 # Optimization solvers (MILP, heuristic)
    domain/
        models/                  # Data models (portfolio, metrics, plan, types)
        ports/                   # Abstract interfaces for providers and repositories
    infrastructure/
        serializer.py            # Serialization/deserialization utilities
        simple_forecast_provider.py
        simple_portfolio_repository.py
    interface/
        endpoints.py             # REST API endpoints (portfolio, load)
        runtime.py               # EMS runtime orchestration and queueing
        server.py                # FastAPI app setup and lifecycle
        websocket.py             # WebSocket endpoint for live updates
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- `pip` for dependency management

### Installation

1. **Clone the repository:**
    ```sh
    git clone <your-repo-url>
    cd <repo-directory>
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the server:**
    ```sh
    python -m ems
    ```
    The API will be available at [http://localhost:8000](http://localhost:8000).

---

## API Overview

- **REST Endpoints** (see `ems/interface/endpoints.py`):
    - `POST /portfolio/` - Create a new portfolio
    - `POST /portfolio/open/{folio_id}` - Open an existing portfolio
    - `PATCH /portfolio/` - Update portfolio parameters
    - `DELETE /portfolio/{folio_id}` - Delete a portfolio
    - `POST /portfolio/plan` - Trigger planning/optimization
    - `POST /load/` - Add a new load
    - `PATCH /load/{load_id}` - Update load parameters
    - `DELETE /load/{load_id}` - Remove a load

- **WebSocket**:
    - `ws://localhost:8000/ws` - Subscribe for real-time EMS context updates

---

## Core Concepts

- **Portfolio**: A collection of loads with optimization parameters (cost vs. emission, priority, etc.).
- **Load**: An energy-consuming asset with status, priority, throughput, and run duration.
- **Metrics**: Time series data for both source (grid/renewable) and load-specific metrics, tracked as forward (planned) and backward (actual).
- **Plan**: The result of an optimization, specifying how loads should be scheduled and supplied.
- **Solvers**: Pluggable optimization engines (MILP and heuristic) for generating feasible and efficient plans.

---

## Development & Testing

- The project is modular and type annotated for clarity and maintainability.
- The main entry point is __main__.py.

To run the tests, follow these steps:

1. Make sure all test files are in a test directory at the project root.
2. Ensure there is an empty `__init__.py` file inside the test directory.
3. From the project root, run a test file using:

    ```sh
    python -m test.test_heuristic_solver
    python -m test.test_milp_solver
    ```

Each test file will print a success message if all tests pass

---

### Cleanup

To safely delete Python bytecode cache directories 
(helpful after running tests or making code changes), run:

```sh
find . -type d -name "__pycache__" -exec rm -r {} +
```
---

## Future Plans: Frontend Dashboard

A major planned extension for this project is a modern, interactive frontend dashboard. This dashboard will allow users to:

- **Visualize energy actuals and forecasts** in real time with clear, intuitive charts and graphs.
- **Manage load schedules** easily through a user-friendly interface.
- **Monitor portfolio performance** and optimization results at a glance.
- **Run schedule optimization** manually if the stale flag is raised.
- **Interact with the EMS** using the existing REST API and WebSocket endpoints.

The current REST API and WebSocket streaming are designed to fully support such a frontend. 
Once implemented, the dashboard will provide a seamless experience 
for both monitoring and managing energy portfolios.

---

## License

This project is distributed under the terms of the GNU General Public License v3.0, 
which guarantees the freedom to use, study, modify, and share the software

**Author:** Rayen Nait Slimane

---

## Acknowledgements

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [PuLP](https://coin-or.github.io/pulp/).
- Designed for extensibility and clarity in energy management simulation and optimization.
