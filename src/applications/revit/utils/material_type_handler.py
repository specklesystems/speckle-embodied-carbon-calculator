from typing import Dict, Any
from enum import Enum
from abc import ABC, abstractmethod
from src.core.types.material_data import MaterialData
from src.applications.revit.utils.constants import (
    VALUE,
    DENSITY,
    STRUCTURAL_ASSET,
    UNITS,
    MATERIAL_NAME,
    COMPRESSIVE_STRENGTH,
)


class MaterialType(Enum):
    CONCRETE = "Concrete"
    METAL = "Metal"
    WOOD = "Wood"


class MaterialTypeHandler(ABC):
    """Abstract base class for handling different material types"""

    @abstractmethod
    def create_material_data(
        self, material_data: Dict[str, Any], volume: float
    ) -> MaterialData:
        pass


class ConcreteHandler(MaterialTypeHandler):
    def create_material_data(
        self, material_data: Dict[str, Any], volume: float
    ) -> MaterialData:
        if DENSITY not in material_data:
            raise ValueError("Missing density in concrete")
        density_dict = material_data[DENSITY]

        if COMPRESSIVE_STRENGTH not in material_data:
            raise ValueError("Missing compression strength in concrete")
        compressive_strength_dict = material_data[COMPRESSIVE_STRENGTH]

        density = density_dict[VALUE]
        comp_strength_units = compressive_strength_dict[UNITS]
        comp_strength_value = compressive_strength_dict[VALUE]

        if comp_strength_units != "Kilonewtons per square meter":
            raise ValueError(f"Unsupported units: {comp_strength_units}")

        grade = comp_strength_value * 0.001  # Convert to MPa

        return MaterialData(
            type=MaterialType.CONCRETE.value,
            volume=volume,
            structural_asset=material_data[STRUCTURAL_ASSET],
            density=density,
            mass=volume * density,
            grade=str(grade),
        )


class MetalHandler(MaterialTypeHandler):
    def create_material_data(
        self, material_data: Dict[str, Any], volume: float
    ) -> MaterialData:
        if "steel" not in material_data[MATERIAL_NAME].lower():
            raise ValueError(
                f"Material name '{material_data[MATERIAL_NAME]}' does not contain 'steel'"
            )

        density = material_data[DENSITY][VALUE]

        return MaterialData(
            type=MaterialType.METAL.value,
            volume=volume,
            structural_asset=material_data[STRUCTURAL_ASSET],
            density=density,
            mass=density * volume,
            grade=material_data[STRUCTURAL_ASSET],
        )


class WoodHandler(MaterialTypeHandler):
    def create_material_data(
        self, material_data: Dict[str, Any], volume: float
    ) -> MaterialData:
        return MaterialData(type=MaterialType.WOOD.value, volume=volume)
