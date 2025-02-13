from dataclasses import dataclass
from typing import Optional


@dataclass
class MaterialData:
    """Data class for material properties"""

    type: str  # Concrete / Steel / Wood
    volume: float
    structural_asset: Optional[str] = None  # Not ideal, but we're being forgiving
    density: Optional[float] = None  # Only needed for steel
    mass: Optional[float] = None  # Only needed for steel
    grade: Optional[str] = None  # Needed for concrete
