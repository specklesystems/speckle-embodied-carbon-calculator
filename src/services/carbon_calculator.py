from typing import Dict

from src.domain.types import BuildingElement, CarbonResult, Material, MaterialType


class CarbonCalculator:
    """Calculates embodied carbon for building elements."""

    def __init__(self):
        # Carbon factors (kgCO2e/kg for metals, kgCO2e/m3 for wood)
        self.metal_factors = {
            "Hot Rolled": 1.22,
            "HSS": 1.99,
            "Plate": 1.73,
            "Rebar": 0.854,
            "default": 1.22,  # Default to hot rolled
        }

        self.wood_factors = {
            "CLT": 135,
            "Glulam": 113,
            "default": 135,  # Default to CLT
        }

    def calculate_carbon(self, element: BuildingElement) -> Dict[str, CarbonResult]:
        """Calculate carbon emissions for an element's materials."""
        results = {}

        for material in element.materials:
            try:
                result = self._calculate_material_carbon(material)
                results[material.properties.name] = result
            except Exception as e:
                # Log error but continue with other materials
                print(
                    f"Error calculating carbon for {material.properties.name}: {str(e)}"
                )

        return results

    def _calculate_material_carbon(self, material: Material) -> CarbonResult:
        """Calculate carbon emissions for a single material."""
        if material.type == MaterialType.METAL:
            return self._calculate_metal_carbon(material)
        elif material.type == MaterialType.WOOD:
            return self._calculate_wood_carbon(material)
        elif material.type == MaterialType.CONCRETE:
            return self._calculate_concrete_carbon(material)
        else:
            raise ValueError(f"Unsupported material type: {material.type}")

    def _calculate_metal_carbon(self, material: Material) -> CarbonResult:
        """Calculate carbon emissions for metal."""
        if not material.mass:
            raise ValueError("Mass required for metal carbon calculation")

        # Determine factor based on grade or use default
        factor = self.metal_factors.get(material.grade, self.metal_factors["default"])

        return CarbonResult(
            factor=factor, total_carbon=material.mass * factor, category="Metal"
        )

    def _calculate_wood_carbon(self, material: Material) -> CarbonResult:
        """Calculate carbon emissions for wood."""
        # Determine factor based on structural asset or use default
        factor = self.wood_factors.get(
            material.properties.structural_asset, self.wood_factors["default"]
        )

        return CarbonResult(
            factor=factor,
            total_carbon=material.properties.volume * factor,
            category="Wood",
        )

    @staticmethod
    def _calculate_concrete_carbon(material: Material) -> CarbonResult:
        """Calculate carbon emissions for concrete."""
        # TODO: Implement concrete-specific carbon calculation
        # This would involve looking up factors based on concrete grade
        # and calculating based on volume or mass depending on the data source
        return CarbonResult(
            factor=0.0,  # Placeholder
            total_carbon=0.0,  # Placeholder
            category="Concrete",
        )
