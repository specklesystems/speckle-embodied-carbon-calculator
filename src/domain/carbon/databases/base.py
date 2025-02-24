from abc import ABC, abstractmethod
from typing import Optional, Dict
from src.domain.carbon.schema import EmissionFactor


class EmissionFactorDatabase(ABC):
    """Base class for emission factor databases"""

    def __init__(self):
        self._factors: Dict[str, EmissionFactor] = {}
        self._material_aliases: Dict[str, list[str]] = {}

    @abstractmethod
    def get_factor(self, material_name: str) -> Optional[EmissionFactor]:
        """Get emission factor for a material name"""
        pass

    def _normalize_material_name(self, name: str) -> str:
        """Normalize material name using aliases"""
        normalized = name.lower()
        for standard, variations in self._material_aliases.items():
            for variation in variations:
                if variation in normalized:
                    normalized = normalized.replace(variation, standard)
        return normalized
