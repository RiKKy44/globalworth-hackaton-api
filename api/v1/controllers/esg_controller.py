from datetime import date
from typing import Optional, List
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from core.database import get_db
from core.security import get_current_user

# ----------------------------
# Modele Pydantic (walidacja danych)
# ----------------------------

class ESGDataResponse(BaseModel):
    co2_emissions_kg: float
    energy_kwh: float
    water_m3: float
    waste_kg: float
    air_quality: dict
    goals: dict

class Sensor(BaseModel):
    sensor_id: str
    type: str
    last_value: float
    unit: str
    last_update: Optional[str]

class AlertConfig(BaseModel):
    sensor_type: str
    threshold: float
    notify_emails: List[str]

class ReportRequest(BaseModel):
    report_type: str
    building_id: str
    year: int
    format: str

class OffsetPurchase(BaseModel):
    tenant_id: str
    co2_amount_kg: float
    provider: str

# ----------------------------
# Funkcje kontrolera
# ----------------------------

async def get_esg_data(
    building_id: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> ESGDataResponse:
    """
    Pobiera dane ESG dla budynku z uwzględnieniem filtrów czasowych.
    
    Args:
        building_id: ID budynku (np. "building_123")
        date_from: Data początkowa (opcjonalna)
        date_to: Data końcowa (opcjonalna)
        db: Sesja bazy danych
        current_user: Zalogowany użytkownik (JWT)
    
    Returns:
        ESGDataResponse: Dane ESG w formacie JSON
    
    Raises:
        HTTPException 404: Jeśli budynek nie istnieje
        HTTPException 403: Brak uprawnień
    """
    # Przykładowa logika (w praktyce zapytanie do DB/czujników)
    if building_id != "building_123":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budynek nie istnieje"
        )
    
    return ESGDataResponse(
        co2_emissions_kg=1200,
        energy_kwh=5000,
        water_m3=200,
        waste_kg=150,
        air_quality={
            "co2_ppm": 800,
            "pm2_5": 12,
            "temperature_c": 22.5
        },
        goals={
            "target_co2_kg": 900,
            "progress": 75
        }
    )

async def list_building_sensors(
    building_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[Sensor]:
    """
    Zwraca listę wszystkich czujników w budynku.
    """
    # Przykładowe dane - w praktyce zapytanie do DB
    return [
        Sensor(
            sensor_id="temp-1a",
            type="temperature",
            last_value=22.5,
            unit="C",
            last_update="2025-03-30T12:00:00Z"
        ),
        Sensor(
            sensor_id="co2-2b",
            type="co2",
            last_value=800,
            unit="ppm",
            last_update=None
        )
    ]

async def create_alert(
    building_id: str,
    alert_config: AlertConfig,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Ustawia próg alertu dla czujnika w budynku.
    """
    if current_user["role"] not in ["tenant_admin", "building_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień"
        )
    
    # Tutaj logika zapisu do DB
    return {
        "status": "alert_created",
        "alert_id": f"alert-{building_id}-{alert_config.sensor_type}"
    }

async def generate_esg_report(
    report_request: ReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Generuje raport ESG w wybranym formacie (PDF/JSON).
    """
    if report_request.report_type != "csrd":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieobsługiwany typ raportu"
        )
    
    # Przykładowe dane raportu
    report_data = {
        "total_co2_emissions": 1200,
        "energy_consumption": 5000,
        "renewable_energy_percentage": 35,
        "water_consumption": 200
    }
    
    if report_request.format == "json":
        return report_data
    else:
        # Tutaj logika generowania PDF (np. użyj reportlab)
        return {
            "status": "pdf_report_generated",
            "download_url": f"/reports/{report_request.building_id}.pdf"
        }

async def purchase_carbon_offsets(
    offset_data: OffsetPurchase,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Realizuje zakup offsetów węglowych.
    """
    # Symulacja transakcji
    return {
        "transaction_id": f"txn-{offset_data.tenant_id[:4]}",
        "co2_offset_kg": offset_data.co2_amount_kg,
        "certificate_url": f"https://offsets.globalworth.com/txn-{offset_data.tenant_id[:4]}.pdf",
        "cost_eur": offset_data.co2_amount_kg * 0.05  # 5 EUR/tonę
    }