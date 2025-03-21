from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List

class MaterialType(Enum):
    CONCRETE = "Concrete"
    METAL = "Metal"
    WOOD = "Wood"

class ElementCategory(Enum):
    SLAB = "Slabs"
    WALL = "Walls"
    COLUMN = "Columns"
    BEAM = "Beams"
    FOUNDATION = "Foundations"

@dataclass
class MaterialProperties:
    name: str
    volume: float
    density: Optional[float] = None
    structural_asset: Optional[str] = None
    compressive_strength: Optional[float] = None

@dataclass
class Material:
    type: MaterialType
    properties: MaterialProperties
    grade: Optional[str] = None
    mass: Optional[float] = None

@dataclass
class BuildingElement:
    id: str
    level: str
    category: ElementCategory
    materials: List[Material]
    carbon_data: Optional[Dict] = None


@dataclass
class CarbonResult:
    factor: float  # kgCO2e/kg for metals, kgCO2e/m3 for wood
    total_carbon: float  # kgCO2e
    category: str

    # Additional fields for detailed output
    quantity: float = None  # volume (m³) for concrete/wood, mass (kg) for metal
    database: str = None  # database source

    # Concrete-specific fields
    concrete_volume: float = None  # m³
    concrete_carbon: float = None  # kgCO2e
    reinforcement_mass: float = None  # kg
    reinforcement_rate: float = None  # kg/m³
    reinforcement_factor: float = None  # kgCO2e/kg
    reinforcement_carbon: float = None  # kgCO2e