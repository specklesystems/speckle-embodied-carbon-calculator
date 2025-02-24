from typing import Dict, Optional

from src.domain.carbon.emission_factor_registry import EmissionFactorRegistry
from src.domain.types import BuildingElement, CarbonResult, Material, MaterialType


class CarbonCalculator:
    """Calculates embodied carbon for building elements."""

    def __init__(
        self,
        steel_database: str,
        timber_database: str,
        concrete_database: Optional[str] = None,
    ):
        # Store database selections
        self._steel_database = steel_database
        self._timber_database = timber_database
        self._concrete_database = concrete_database

        # Initialize registry
        self._registry = EmissionFactorRegistry()

        # Cache common material factors to avoid repeated lookups
        self._steel_factors_cache = {}
        self._timber_factors_cache = {}
        self._concrete_factors_cache = {}

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

        # Get factor from cache or registry
        if material.grade not in self._steel_factors_cache:
            factor = self._registry.get_steel_factor(
                material.grade, self._steel_database
            )
            if not factor:
                raise ValueError(
                    f"No emission factor found for metal grade: {material.grade}"
                )
            self._steel_factors_cache[material.grade] = factor

        factor = self._steel_factors_cache[material.grade]
        return CarbonResult(
            factor=factor.value,
            total_carbon=material.mass * factor.value,
            category="Metal",
        )

    def _calculate_wood_carbon(self, material: Material) -> CarbonResult:
        """Calculate carbon emissions for wood."""
        structural_asset = material.properties.structural_asset

        # Get factor from cache or registry
        if structural_asset not in self._timber_factors_cache:
            factor = self._registry.get_timber_factor(
                structural_asset, self._timber_database
            )
            if not factor:
                raise ValueError(
                    f"No emission factor found for wood type: {structural_asset}"
                )
            self._timber_factors_cache[structural_asset] = factor

        factor = self._timber_factors_cache[structural_asset]
        return CarbonResult(
            factor=factor.value,
            total_carbon=material.properties.volume * factor.value,
            category="Wood",
        )

    def _calculate_concrete_carbon(self, material: Material) -> CarbonResult:
        """Calculate carbon emissions for concrete."""
        # TODO: Implement concrete-specific calculation when concrete database is added
        return CarbonResult(
            factor=0.0,  # Placeholder
            total_carbon=0.0,  # Placeholder
            category="Concrete",
        )
