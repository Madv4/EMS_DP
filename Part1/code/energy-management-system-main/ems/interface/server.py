from fastapi import FastAPI

# from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from ems.interface.runtime import start_services, stop_services
from ems.interface.endpoints import portfolio_router, load_router
from ems.interface.websocket import ws_endpoint
from ems.infrastructure.simple_forecast_provider import SimpleForecastProvider
from ems.infrastructure.simple_portfolio_repository import SimplePortfolioRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    provider = SimpleForecastProvider()
    repository = SimplePortfolioRepository()
    try:
        await start_services(duration=5, provider=provider, repository=repository)
        yield
    finally:
        await stop_services()


app = FastAPI(lifespan=lifespan)
# app.mount("/", StaticFiles(directory="web", html=True), name="frontend")
app.include_router(portfolio_router)
app.include_router(load_router)
app.add_api_websocket_route("/ws", ws_endpoint)
