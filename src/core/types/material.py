from dataclasses import dataclass
from typing import Optional


@dataclass
class MaterialData:
    """Data class for material properties"""

    volume: float
    density: float
    structural_asset: str
    mass: Optional[float] = None
