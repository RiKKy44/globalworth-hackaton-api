from datetime import datetime
from fastapi import HTTPException, Depends, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Literal
import json
import os
from pathlib import Path
from core.database import get_db
from core.security import get_current_user

# ----------------------------
# Modele Pydantic
# ----------------------------

class ReportRequest(BaseModel):
    report_type: Literal["csrd", "annual", "custom"] = "csrd"
    building_id: str
    year: int
    format: Literal["pdf", "json"] = "json"
    filters: Optional[dict] = None

class ReportResponse(BaseModel):
    report_id: str
    generated_at: datetime
    download_url: str
    format: str
    size_kb: float

# ----------------------------
# Funkcje kontrolera
# ----------------------------

async def generate_report(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generuje raport ESG w wybranym formacie (PDF/JSON).
    
    Args:
        request: ReportRequest - parametry raportu
        db: Sesja bazy danych
        current_user: Dane użytkownika z JWT
    
    Returns:
        FileResponse (PDF) lub JSONResponse
    
    Raises:
        HTTPException 400: Nieprawidłowy typ raportu
        HTTPException 403: Brak uprawnień
    """
    
    # Sprawdzenie uprawnień
    if current_user["role"] not in ["tenant_admin", "building_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wymagane uprawnienia administratora"
        )

    # Pobranie danych z bazy (mock - zastąp rzeczywistym zapytaniem)
    report_data = await _fetch_esg_data(
        db, 
        request.building_id, 
        request.year,
        request.filters
    )

    # Generowanie raportu w wybranym formacie
    if request.format == "json":
        return await _generate_json_report(report_data, request)
    else:
        return await _generate_pdf_report(report_data, request)

# ----------------------------
# Funkcje prywatne
# ----------------------------

async def _fetch_esg_data(
    db: AsyncSession, 
    building_id: str,
    year: int,
    filters: Optional[dict] = None
) -> dict:
    """Pobiera dane ESG z bazy danych"""
    # Mock danych - w praktyce użyj SQLAlchemy
    return {
        "building_id": building_id,
        "year": year,
        "co2_emissions_kg": 1250.5,
        "energy_consumption_kwh": 5240,
        "renewable_energy_percent": 38.7,
        "water_consumption_m3": 215,
        "waste_kg": 180,
        "air_quality_avg": {
            "co2_ppm": 820,
            "pm2_5": 14,
            "temperature_c": 22.3
        }
    }

async def _generate_json_report(
    data: dict,
    request: ReportRequest
) -> JSONResponse:
    """Generuje raport w formacie JSON"""
    report_id = f"report_{request.building_id}_{datetime.now().strftime('%Y%m%d%H%M')}"
    
    response_data = {
        "report_id": report_id,
        "type": request.report_type,
        "data": data,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "format": "json",
            "version": "1.0"
        }
    }
    
    return JSONResponse(content=response_data)

async def _generate_pdf_report(
    data: dict,
    request: ReportRequest
) -> FileResponse:
    """Generuje raport PDF (mock - w praktyce użyj reportlab/weasyprint)"""
    from fpdf import FPDF  # Mock - zainstaluj fpdf2
    
    # Tworzenie PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Nagłówek
    pdf.cell(200, 10, txt=f"Raport ESG - Budynek {request.building_id}", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Rok: {request.year}", ln=1, align='C')
    
    # Dane
    for key, value in data.items():
        if isinstance(value, dict):
            pdf.cell(200, 10, txt=f"{key}:", ln=1)
            for subkey, subvalue in value.items():
                pdf.cell(200, 10, txt=f"  {subkey}: {subvalue}", ln=1)
        else:
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=1)
    
    # Zapisz tymczasowo
    report_dir = Path("storage/reports")
    report_dir.mkdir(exist_ok=True)
    filename = f"esg_report_{request.building_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = report_dir / filename
    pdf.output(filepath)
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/pdf"
    )