from typing import Optional, List, Union

from src.domain.types import BuildingElement, ElementCategory, Material
from src.infrastructure.logging import Logging
from src.services.material_processor import MaterialProcessor


class ElementProcessor:
    """Processes Revit building elements."""

    SKIP_TYPES = [
        "Objects.Geometry.Line",
        "Objects.Geometry.Arc",
        "Objects.Geometry.Circle",
    ]

    SKIP_FAMILIES = ["Grid", "JS_SF_Centerline Only"]

    def __init__(self, material_processor: MaterialProcessor, logger: Logging):
        self.material_processor = material_processor
        self.logger = logger

    def process_element(self, element: dict) -> Optional[BuildingElement]:
        """Process a single Revit element."""
        try:
            # Skip basic geometric types
            if self.is_skipped(element):
                return None  # Skipped elements return None

            # Basic validation
            if not self.is_valid_element(element):
                return None  # Invalid elements also return None, but we'll handle them differently

            # Extract basic properties
            element_id = getattr(element, "id", "unknown")
            level = self._get_element_level(element)
            category = self._determine_category(element)

            # Process materials
            materials = self._process_materials(element)

            # Create building element
            return BuildingElement(
                id=element_id, level=level, category=category, materials=materials
            )

        except Exception as e:
            self.logger.log_error(
                getattr(element, "id"),
                "Element Processing",
                f"Error processing element {getattr(element, 'id')}: {str(e)}",
            )
            return None

    def is_skipped(self, element) -> bool:
        """Skipping non-model objects."""
        if getattr(element, "speckle_type", None) in self.SKIP_TYPES:
            return True
        if getattr(element, "family", None) in self.SKIP_FAMILIES:
            return True
        return False

    @staticmethod
    def is_valid_element(element) -> bool:
        """Validate if element should be processed."""

        # Must have properties
        if not hasattr(element, "properties"):
            return False

        # Must have material quantities
        properties = getattr(element, "properties")
        if "Material Quantities" not in properties:
            return False

        return True

    @staticmethod
    def _get_element_level(element) -> str:
        """Extract element level."""
        return getattr(element, "level", "Unknown")

    @staticmethod
    def _determine_category(element: dict) -> ElementCategory:
        """Determine element category based on type name."""
        type_name = getattr(element, "name", "").lower()

        category_mapping = {
            "floor": ElementCategory.SLAB,
            "stair": ElementCategory.SLAB,
            "slab": ElementCategory.SLAB,
            "wall": ElementCategory.WALL,
            "column": ElementCategory.COLUMN,
            "beam": ElementCategory.BEAM,
            "framing": ElementCategory.BEAM,
            "foundation": ElementCategory.FOUNDATION,
        }

        for key, category in category_mapping.items():
            if key in type_name:
                return category

        return ElementCategory.BEAM  # Default category

    def _process_materials(self, element) -> List[Material]:
        """Process all materials in the element."""
        materials = []
        properties = getattr(element, "properties")
        material_quantities = properties["Material Quantities"]

        for material_data in material_quantities.values():  # Added .values()
            try:
                material = self.material_processor.process_material(material_data)
                materials.append(material)
            except Exception as e:
                self.logger.log_warning(
                    getattr(element, "id"),
                    "Material Processing",
                    f"Failed to process material in element {getattr(element, 'id')}: {str(e)}",
                )

        return materials
