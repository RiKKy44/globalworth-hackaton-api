from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.building import (
    BuildingCreate,
    BuildingResponse,
    BuildingCRUD,
    get_building_or_404,
    DBBuilding
)
import datetime
from core.database import get_db
from core.security import get_current_user

class BuildingResponse(BuildingBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
router = APIRouter(prefix="/buildings", tags=["Buildings"])

@router.post("/", response_model=BuildingResponse)
async def create_building(
    building: BuildingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new building (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create buildings"
        )
    return await BuildingCRUD.create(db, building)

@router.get("/{building_id}", response_model=BuildingResponse)
async def read_building(
    building: DBBuilding = Depends(get_building_or_404)
):
    """Get building by ID"""
    return building

@router.get("/", response_model=List[BuildingResponse])  # Use List[] for type hinting
async def list_buildings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all buildings"""
    return await BuildingCRUD.get_all(db, skip, limit)

@router.put("/{building_id}", response_model=BuildingResponse)
async def update_building(
    update_data: BuildingCreate,
    building: DBBuilding = Depends(get_building_or_404),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update building details"""
    if current_user["role"] not in ["admin", "building_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return await BuildingCRUD.update(db, building.id, update_data.dict())

@router.delete("/{building_id}")
async def delete_building(
    building: DBBuilding = Depends(get_building_or_404),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete building (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = await BuildingCRUD.delete(db, building.id)
    return {"deleted": success}