from typing import Dict, Optional, Tuple, List

from src.domain.carbon.concrete_reinforcement import ReinforcementRates
from src.domain.carbon.emission_factor_registry import EmissionFactorRegistry
from src.domain.types import (
    BuildingElement,
    CarbonResult,
    Material,
    MaterialType,
    ElementCategory,
)


class CarbonCalculator:
    """Calculates embodied carbon for building elements."""

    def __init__(
        self,
        steel_database: str,
        timber_database: str,
        concrete_database: str,
        country: str,
        custom_reinforcement_rates: Dict[str, float],
    ):
        # Store database selections
        self._steel_database = steel_database
        self._timber_database = timber_database
        self._concrete_database = concrete_database
        self._country = country

        # Initialize registry
        self._registry = EmissionFactorRegistry()

        # Initialize reinforcement rates with the provided dictionary
        # TODO: Validate inputs (e.g. C# int.TryParse()? )
        self._reinforcement_rates = ReinforcementRates(custom_reinforcement_rates)

        # Cache common material factors to avoid repeated lookups
        self._steel_factors_cache = {}
        self._timber_factors_cache = {}
        self._concrete_factors_cache = {}

        # Track missing factors
        self._missing_timber_factors = set()
        self._missing_steel_factors = set()
        self._missing_concrete_factors = set()

    def calculate_carbon(self, element: BuildingElement) -> Dict[str, CarbonResult]:
        """Calculate carbon emissions for an element's materials."""
        results = {}

        for material in element.materials:
            try:
                if material.type == MaterialType.CONCRETE:
                    result = self._calculate_concrete_carbon(material, element.category)
                else:
                    result = self._calculate_material_carbon(material)
                results[material.properties.name] = result
            except Exception as e:
                # Track missing factors
                if "No emission factor found" in str(e):
                    if material.type == MaterialType.WOOD:
                        material_key = (
                            material.properties.structural_asset
                            or material.properties.name
                        )
                        self._missing_timber_factors.add(material_key)
                    elif material.type == MaterialType.METAL:
                        self._missing_steel_factors.add(
                            material.grade or material.properties.name
                        )
                    elif material.type == MaterialType.CONCRETE:
                        # Track missing concrete factors
                        strength = str(int(material.properties.compressive_strength))
                        element_type = self._map_element_category_to_concrete_type(
                            element.category
                        )
                        self._missing_concrete_factors.add(f"{strength}_{element_type}")

                print(
                    f"Error calculating carbon for {material.properties.name}: {str(e)}"
                )

        return results

    def _calculate_material_carbon(
        self, material: Material, element_category: Optional[ElementCategory] = None
    ) -> CarbonResult:
        """Calculate carbon emissions for a single material."""
        if material.type == MaterialType.METAL:
            return self._calculate_metal_carbon(material)
        elif material.type == MaterialType.WOOD:
            return self._calculate_wood_carbon(material)
        elif material.type == MaterialType.CONCRETE:
            if element_category is None:
                raise ValueError(
                    "Element category is required for concrete carbon calculation"
                )
            return self._calculate_concrete_carbon(material, element_category)
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
            quantity=material.mass,
            database=self._steel_database,
        )

    def _calculate_wood_carbon(self, material: Material) -> CarbonResult:
        """Calculate carbon emissions for wood."""
        material_name = material.properties.structural_asset

        # Use name as a fallback if structural_asset is None
        if material_name is None:
            # Extract material type from name
            material_name = material.properties.name

        # Get factor from cache or registry
        if material_name not in self._timber_factors_cache:
            factor = self._registry.get_timber_factor(
                material_name, self._timber_database
            )
            if not factor:
                raise ValueError(
                    f"No emission factor found for wood type: {material_name}"
                )
            self._timber_factors_cache[material_name] = factor

        factor = self._timber_factors_cache[material_name]
        return CarbonResult(
            factor=factor.value,
            total_carbon=material.properties.volume * factor.value,
            category="Wood",
            quantity=material.properties.volume,
            database=self._timber_database,
        )

    def _calculate_concrete_carbon(
        self, material: Material, element_category: ElementCategory
    ) -> CarbonResult:
        """Calculate carbon emissions for concrete, including reinforcement."""
        if not material.properties.compressive_strength:
            raise ValueError(
                "Compressive strength required for concrete carbon calculation"
            )

        # Handle unit conversion based on country
        # For US, convert PSI to MPa if needed
        strength_value = material.properties.compressive_strength
        if self._country == "USA":
            # Check if value is in PSI (typically large numbers)
            if strength_value > 100:  # Assume PSI
                strength_value = strength_value / 145.038  # Convert PSI to MPa

        # Round to nearest valid strength category (25, 30, 35, 40, 45, 50)
        valid_strengths = [25, 30, 35, 40, 45, 50]
        strength_mpa = min(valid_strengths, key=lambda x: abs(x - strength_value))
        strength = str(strength_mpa)

        # Map element category to concrete element type for the database
        element_type = self._map_element_category_to_concrete_type(element_category)

        # Create cache key for concrete factors
        concrete_cache_key = f"{strength}_{element_type}"

        # Get concrete factor
        if concrete_cache_key not in self._concrete_factors_cache:
            try:
                factor = self._registry.get_concrete_factor(
                    strength, element_type, self._concrete_database
                )
                if not factor:
                    self._missing_concrete_factors.add(concrete_cache_key)
                    raise ValueError(
                        f"No emission factor found for concrete: strength={strength}, element={element_type}"
                    )
                self._concrete_factors_cache[concrete_cache_key] = factor
            except Exception as e:
                self._missing_concrete_factors.add(concrete_cache_key)
                raise ValueError(f"Error getting concrete factor: {str(e)}")

        concrete_factor = self._concrete_factors_cache[concrete_cache_key]
        concrete_volume = material.properties.volume
        concrete_carbon = concrete_volume * concrete_factor.value

        # Calculate reinforcement carbon
        reinforcement_rate = self._reinforcement_rates.get_rate(element_type)
        reinforcement_mass = (
            concrete_volume * reinforcement_rate / 1000
        )  # Convert kg to tons if needed

        # Get rebar factor from steel database
        if "Rebar" not in self._steel_factors_cache:
            rebar_factor = self._registry.get_steel_factor(
                "Rebar", self._steel_database
            )
            if not rebar_factor:
                raise ValueError("No emission factor found for rebar")
            self._steel_factors_cache["Rebar"] = rebar_factor

        rebar_factor = self._steel_factors_cache["Rebar"]
        reinforcement_carbon = reinforcement_mass * rebar_factor.value

        # Total carbon is concrete + reinforcement
        total_carbon = concrete_carbon + reinforcement_carbon

        # Create result with additional metadata
        return CarbonResult(
            factor=concrete_factor.value,
            total_carbon=total_carbon,
            category="Concrete",
            quantity=concrete_volume,
            database=self._concrete_database,
            concrete_volume=concrete_volume,
            concrete_carbon=concrete_carbon,
            reinforcement_mass=reinforcement_mass,
            reinforcement_rate=reinforcement_rate,
            reinforcement_factor=rebar_factor.value,
            reinforcement_carbon=reinforcement_carbon,
        )

    @staticmethod
    def _map_element_category_to_concrete_type(
        element_category: ElementCategory,
    ) -> str:
        """Map BuildingElement category to concrete element type for database lookup."""

        # Default mappings
        category_mapping = {
            ElementCategory.SLAB: "Slab",
            ElementCategory.WALL: "Wall",
            ElementCategory.COLUMN: "Column",
            ElementCategory.BEAM: "Beam",
            ElementCategory.FOUNDATION: "Foundation",
        }

        # Return the mapped type or default to "Beam" if unknown
        return category_mapping.get(element_category, "Beam")

    def get_missing_factors(self) -> Tuple[List[str], List[str], List[str]]:
        """Return lists of materials that had no emission factor."""
        return (
            sorted(list(self._missing_timber_factors)),
            sorted(list(self._missing_steel_factors)),
            sorted(list(self._missing_concrete_factors)),
        )
