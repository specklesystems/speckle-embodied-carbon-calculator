from typing import Optional
from src.domain.carbon.schema import EmissionDatabase, EmissionFactor
from src.domain.carbon.databases.base import EmissionFactorDatabase


class EPDGlobalDatabase(EmissionFactorDatabase):
    """EPD Global emission factor database implementation"""

    def __init__(self):
        super().__init__()
        self._factors = {
            "hot rolled structural steel": EmissionFactor(
                value=1.22,
                unit="kgCO2e/kg",
                database=EmissionDatabase.EPD_GLOBAL,
                epd_number="EPD-123-2024",
                publication_date="2024-01-01",
                valid_until="2029-01-01",
                manufacturer="SteelCo",
                plant_location="Sheffield, UK",
            ),
            # Add other factors...
        }

        self._material_aliases = {
            "hot rolled": ["hot-rolled", "hot_rolled", "hotrolled"],
            "structural steel": ["structural_steel", "struct steel"],
            # Add other aliases...
        }

    def get_factor(self, material_name: str) -> Optional[EmissionFactor]:
        """Get emission factor for a material name, checking variations"""
        # Try direct match first
        material_name = material_name.lower()
        if material_name in self._factors:
            return self._factors[material_name]

        # Try aliases
        normalized_name = self._normalize_material_name(material_name)
        return self._factors.get(normalized_name)
