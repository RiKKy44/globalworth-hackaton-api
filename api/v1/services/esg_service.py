from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_
from models.esg_metrics import DBEscMetrics, EsgMetricCreate
from core.database import get_db
from fastapi import HTTPException, status, Depends

class ESGService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_metric(self, metric_data: EsgMetricCreate) -> DBEscMetrics:
        """Create new ESG metric entry"""
        try:
            metric = DBEscMetrics(**metric_data.dict())
            self.db.add(metric)
            await self.db.commit()
            await self.db.refresh(metric)
            return metric
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create metric: {str(e)}"
            )

    async def get_metrics_by_building(
        self,
        building_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DBEscMetrics]:
        """Get metrics for a building with optional date range"""
        try:
            query = self.db.query(DBEscMetrics).filter(
                DBEscMetrics.building_id == building_id
            )
            
            if start_date and end_date:
                query = query.filter(
                    and_(
                        DBEscMetrics.timestamp >= start_date,
                        DBEscMetrics.timestamp <= end_date
                    )
                )
            
            result = await self.db.execute(
                query.order_by(DBEscMetrics.timestamp.desc()).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching metrics: {str(e)}"
            )

    async def get_aggregated_data(
        self,
        building_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """Get aggregated ESG data for reporting"""
        try:
            result = await self.db.execute(
                self.db.query(
                    func.sum(DBEscMetrics.co2_kg).label("total_co2"),
                    func.sum(DBEscMetrics.energy_kwh).label("total_energy"),
                    func.sum(DBEscMetrics.water_m3).label("total_water"),
                    func.sum(DBEscMetrics.waste_kg).label("total_waste")
                ).filter(
                    DBEscMetrics.building_id == building_id,
                    DBEscMetrics.timestamp >= start_date,
                    DBEscMetrics.timestamp <= end_date
                )
            )
            return result.mappings().one()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for given criteria: {str(e)}"
            )

# Dependency
async def get_esg_service(db: AsyncSession = Depends(get_db)):
    yield ESGService(db)