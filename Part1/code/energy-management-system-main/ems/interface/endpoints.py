# api/endpoints/portfolio.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Tuple
import uuid
from ems.application.services.ems_service import (
    plan,
    create_portfolio,
    open_portfolio,
    patch_portfolio,
    delete_portfolio,
    add_load,
    patch_load,
    remove_load,
)

# queue-based actor dispatcher
from ems.interface.runtime import get_runtime


portfolio_router = APIRouter(prefix="/portfolio")
load_router = APIRouter(prefix="/load")


# Request models


class PatchPortfolioRequest(BaseModel):
    cost_vs_emission_weight: Optional[float] = None
    emission_coeff: Optional[float] = None
    priority_coeff: Optional[float] = None


class PatchLoadRequest(BaseModel):
    toggle: Optional[bool] = None
    confirm: Optional[bool] = None
    priority: Optional[int] = None
    throughput: Optional[Tuple[float, float]] = None
    run_duration: Optional[int] = None


# Portfolio routes


@portfolio_router.post("/")
async def create_portfolio_api(dispatcher=Depends(get_runtime)):
    return await dispatcher.submit(create_portfolio)


@portfolio_router.post("/open/{folio_id}")
async def open_portfolio_api(folio_id: str, dispatcher=Depends(get_runtime)):
    try:
        fid = uuid.UUID(folio_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid folio_id")
    return await dispatcher.submit(open_portfolio, fid)


@portfolio_router.patch("/")
async def patch_portfolio_api(
    payload: PatchPortfolioRequest, dispatcher=Depends(get_runtime)
):
    return await dispatcher.submit(
        patch_portfolio,
        payload.cost_vs_emission_weight,
        payload.emission_coeff,
        payload.priority_coeff,
    )


@portfolio_router.delete("/{folio_id}")
async def delete_portfolio_api(folio_id: str, dispatcher=Depends(get_runtime)):
    try:
        fid = uuid.UUID(folio_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid folio_id")
    return await dispatcher.submit(delete_portfolio, fid)


@portfolio_router.post("/plan")
async def plan_api(dispatcher=Depends(get_runtime)):
    return await dispatcher.submit(plan)


# Load routes


@load_router.post("/")
async def add_load_api(dispatcher=Depends(get_runtime)):
    return await dispatcher.submit(add_load)


@load_router.patch("/{load_id}")
async def patch_load_api(
    load_id: str, payload: PatchLoadRequest, dispatcher=Depends(get_runtime)
):
    try:
        lid = uuid.UUID(load_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid load_id")
    return await dispatcher.submit(
        patch_load,
        lid,
        payload.toggle,
        payload.confirm,
        payload.priority,
        payload.throughput,
        payload.run_duration,
    )


@load_router.delete("/{load_id}")
async def remove_load_api(load_id: str, dispatcher=Depends(get_runtime)):
    try:
        lid = uuid.UUID(load_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid load_id")
    return await dispatcher.submit(remove_load, lid)
