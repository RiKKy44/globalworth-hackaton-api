from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base
import uuid
from sqlalchemy import func

Base = declarative_base()

# ----------------------------
# Database Model (SQLAlchemy)
# ----------------------------

class DBEscMetrics(Base):
    """Raw ESG metrics storage"""
    __tablename__ = "esg_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id = Column(String(36), ForeignKey("buildings.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    co2_kg = Column(Float, nullable=False)  # CO2 emissions in kilograms
    energy_kwh = Column(Float, nullable=False)
    water_m3 = Column(Float, nullable=False)
    waste_kg = Column(Float, nullable=False)

# ----------------------------
# Pydantic Models (API)
# ----------------------------

class EsgMetricBase(BaseModel):
    building_id: str
    co2_kg: float = Field(..., gt=0, example=1200.5, description="CO2 emissions in kilograms")
    energy_kwh: float = Field(..., gt=0, example=5000)
    water_m3: float = Field(..., gt=0, example=200)
    waste_kg: float = Field(..., gt=0, example=150)
    timestamp: Optional[datetime] = None

    @validator('timestamp')
    def set_timestamp(cls, v):
        return v or datetime.utcnow()

class EsgMetricCreate(EsgMetricBase):
    pass

class EsgMetricResponse(EsgMetricBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

# ----------------------------
# CRUD Operations
# ----------------------------

class EsgMetricsCRUD:
    """Handles all database operations for ESG metrics"""
    
    @staticmethod
    async def create(db: AsyncSession, metric: EsgMetricCreate) -> DBEscMetrics:
        db_metric = DBEscMetrics(**metric.dict())
        db.add(db_metric)
        await db.commit()
        await db.refresh(db_metric)
        return db_metric

    @staticmethod
    async def get_latest(
        db: AsyncSession, 
        building_id: str,
        limit: int = 100
    ) -> list[DBEscMetrics]:
        result = await db.execute(
            select(DBEscMetrics)
            .where(DBEscMetrics.building_id == building_id)
            .order_by(DBEscMetrics.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_aggregates(
        db: AsyncSession,
        building_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """Returns sum of metrics for a date range"""
        result = await db.execute(
            select(
                func.sum(DBEscMetrics.co2_kg).label("total_co2"),
                func.sum(DBEscMetrics.energy_kwh).label("total_energy"),
                func.sum(DBEscMetrics.water_m3).label("total_water"),
                func.sum(DBEscMetrics.waste_kg).label("total_waste")
            )
            .where(DBEscMetrics.building_id == building_id)
            .where(DBEscMetrics.timestamp >= start_date)
            .where(DBEscMetrics.timestamp <= end_date)
        )
        return result.mappings().one()