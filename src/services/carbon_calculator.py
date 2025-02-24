from typing import Dict

from src.domain.carbon.registry import EmissionFactorRegistry
from src.domain.carbon.schema import EmissionDatabase, EmissionFactor
from src.domain.types import BuildingElement, CarbonResult, Material, MaterialType


class CarbonCalculator:
    """Calculates embodied carbon for building elements."""

    def __init__(
        self,
        metal_database: EmissionDatabase,
        wood_database: EmissionDatabase,
        registry: EmissionFactorRegistry,
    ):
        self._registry = registry
        self._metal_factors: dict[str, EmissionFactor] = {}
        self._wood_factors: dict[str, EmissionFactor] = {}

        # Cache all metal factors
        for grade in [
            "Hot Rolled",
            "HSS",
            "Plate",
            "Rebar",
            "OWSJ",
            "Fasteners",
            "Metal Deck",
        ]:
            factor = self._registry.get_factor(grade, metal_database)
            if factor:
                self._metal_factors[grade] = factor

        # Cache all wood factors
        for wood_type in [
            "CLT",
            "Glulam",
            "LVL",
            "Softwood Lumber",
            "Softwood Plywood",
        ]:
            factor = self._registry.get_factor(wood_type, wood_database)
            if factor:
                self._wood_factors[wood_type] = factor

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

        factor = self._metal_factors.get(material.grade)
        if not factor:
            raise ValueError(
                f"No emission factor found for metal grade: {material.grade}"
            )

        return CarbonResult(
            factor=factor.value,
            total_carbon=material.mass * factor.value,
            category="Metal",
        )

    def _calculate_wood_carbon(self, material: Material) -> CarbonResult:
        """Calculate carbon emissions for wood."""
        # Determine factor based on structural asset or use default
        factor = self._wood_factors.get(material.properties.structural_asset)
        if not factor:
            raise ValueError(
                f"No emission factor found for wood type: {material.properties.structural_asset}"
            )

        return CarbonResult(
            factor=factor.value,
            total_carbon=material.properties.volume * factor.value,
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
