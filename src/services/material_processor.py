from typing import Dict, Any

from src.domain.types import MaterialProperties, Material, MaterialType


class MaterialProcessor:
    """Processes Revit materials and calculates quantities."""

    DEFAULT_CONCRETE_GRADE = "35"
    DEFAULT_STEEL_DENSITY = 7851.81483993  # kg/m3

    def process_material(self, raw_material: Dict[str, Any]) -> Material:
        """Process raw material data from Revit into domain model."""
        properties = MaterialProperties(
            name=raw_material["materialName"],
            volume=raw_material["volume"]["value"],
            density=raw_material.get("density", {}).get(
                "value"
            ),  # Using .get() for optional fields
            structural_asset=raw_material.get("structuralAsset"),
            compressive_strength=raw_material.get("compressiveStrength", {}).get(
                "value"
            ),
        )

        # Determine material type and create material
        if self._is_high_grade_material(raw_material):
            return self._process_high_grade_material(properties)
        else:
            return self._process_low_grade_material(properties)

    @staticmethod
    def _is_high_grade_material(raw_material: Dict[str, Any]) -> bool:
        return "structuralAsset" in raw_material

    def _process_high_grade_material(self, props: MaterialProperties) -> Material:
        """Process materials with structural assets."""
        if "concrete" in props.name.lower():
            return self._process_concrete(props)
        elif "steel" in props.name.lower():
            return self._process_steel(props)
        elif "clt" in props.name.lower() or "timber" in props.name.lower():
            return Material(type=MaterialType.WOOD, properties=props)
        else:
            raise ValueError(f"Unknown high-grade material: {props.name}")

    def _process_low_grade_material(self, props: MaterialProperties) -> Material:
        """Process materials without structural assets."""
        name = props.name.lower()

        if "concrete" in name:
            return Material(
                type=MaterialType.CONCRETE,
                properties=props,
                grade=self.DEFAULT_CONCRETE_GRADE,
            )
        elif "steel" in name:
            mass = props.volume * self.DEFAULT_STEEL_DENSITY
            return Material(
                type=MaterialType.METAL,
                properties=props,
                mass=mass,
                grade="default_steel",
            )
        elif "clt" in name or "timber" in name:
            return Material(type=MaterialType.WOOD, properties=props)
        else:
            raise ValueError(f"Unknown material type: {props.name}")

    @staticmethod
    def _process_concrete(props: MaterialProperties) -> Material:
        """Process concrete-specific properties."""
        if not props.compressive_strength:
            raise ValueError("Missing compressive strength for concrete")

        grade = str(props.compressive_strength * 0.001)  # Convert to MPa
        return Material(type=MaterialType.CONCRETE, properties=props, grade=grade)

    @staticmethod
    def _process_steel(props: MaterialProperties) -> Material:
        """Process steel-specific properties."""
        if not props.density:
            raise ValueError("Missing density for steel")

        mass = props.volume * props.density
        return Material(
            type=MaterialType.METAL,
            properties=props,
            mass=mass,
            grade=props.structural_asset,
        )
