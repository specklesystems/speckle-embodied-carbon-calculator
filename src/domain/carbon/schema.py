from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EmissionDatabase(str, Enum):
    """Available emission factor databases"""

    EPD_GLOBAL = "EPD Global"
    ICE = "Inventory of Carbon and Energy"
    EC3 = "EC3 Database"


@dataclass
class EmissionFactor:
    """Emission factor with metadata"""

    value: float
    unit: str  # e.g., "kgCO2e/kg" or "kgCO2e/m3"
    database: EmissionDatabase
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
