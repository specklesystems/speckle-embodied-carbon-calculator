from abc import ABC
from typing import Optional, Dict
from src.domain.carbon.schema import EmissionFactor


class EmissionFactorDatabase(ABC):
    """Base class for emission factor databases"""

    def __init__(self):
        self._factors: Dict[str, EmissionFactor] = {}

    def get_factor(self, material_name: str) -> Optional[EmissionFactor]:
        """Get emission factor for a material name"""
        material_name = material_name.lower()
        for name, factor in self._factors.items():
            if name.lower() == material_name:
                return factor

        # If no direct match, return None
        return None
