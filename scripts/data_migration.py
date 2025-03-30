
import argparse
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db, Base, async_session
from api.v1.models.esg_metrics import DBEscMetrics, EsgMetricCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_from_csv(file_path: Path, batch_size: int = 100):
    """Migrate data from CSV to database"""
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            batch = []
            
            async with async_session() as session:
                for row in reader:
                    try:
                        metric = EsgMetricCreate(
                            building_id=row['building_id'],
                            co2_kg=float(row['co2_kg']),
                            energy_kwh=float(row['energy_kwh']),
                            water_m3=float(row['water_m3']),
                            waste_kg=float(row['waste_kg']),
                            timestamp=datetime.fromisoformat(row['timestamp'])
                        )
                        batch.append(DBEscMetrics(**metric.dict()))
                        
                        if len(batch) >= batch_size:
                            session.add_all(batch)
                            await session.commit()
                            batch = []
                            logger.info(f"Migrated {batch_size} records")
                            
                    except Exception as e:
                        logger.error(f"Skipping invalid row: {str(e)}")
                        continue
                
                if batch:
                    session.add_all(batch)
                    await session.commit()
                    logger.info(f"Migrated final {len(batch)} records")
                
                logger.info("Migration completed successfully")

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ESG Data Migration Tool')
    parser.add_argument('file', type=str, help='Path to CSV file')
    parser.add_argument('--batch-size', type=int, default=100, 
                      help='Number of records per batch')
    
    args = parser.parse_args()
    asyncio.run(migrate_from_csv(Path(args.file), args.batch_size))