from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import AdminDep, BuildingManagerDep
from models.esg_metrics import EsgMetricCreate, EsgMetricsCRUD

router = APIRouter(prefix="/esg", tags=["ESG Data"])

@router.post("/metrics")
async def create_esg_metric(
    metric: EsgMetricCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, AdminDep]  # Enforces admin role
):
    try:
        return await EsgMetricsCRUD.create(db, metric)
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@router.get("/metrics/{building_id}")
async def get_esg_metrics(
    building_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, BuildingManagerDep]  # Enforces manager role
):
    try:
        return await EsgMetricsCRUD.get_by_building(db, building_id)
    except Exception as e:
        raise HTTPException(500, detail=str(e))