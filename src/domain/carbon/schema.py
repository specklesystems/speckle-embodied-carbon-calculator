from dataclasses import dataclass
from typing import Optional


@dataclass
class EmissionFactor:
    """Emission factor with metadata"""

    value: float
    unit: str  # e.g., "kgCO2e/kg" or "kgCO2e/m3"
    database: str
    epd_number: Optional[str] = None
    publication_date: Optional[str] = None
    valid_until: Optional[str] = None
    manufacturer: Optional[str] = None
    plant_location: Optional[str] = None


@dataclass
class CarbonResult:
    """Result of a carbon calculation"""

    material_name: str
    emission_factor: EmissionFactor
    quantity: float
    total_carbon: float
    category: str
