from typing import Generator, Any, Tuple
from src.core.base import MaterialProcessor, Compliance, CarbonProcessor
from src.core.base.logger import Logger
from src.applications.revit.utils.constants import (
    ELEMENTS,
    NAME,
    ID,
    MATERIAL_QUANTITIES,
    PROPERTIES,
)


class RevitElementProcessor:
    """Processes Revit model elements to extract and analyze material data."""

    def __init__(
        self,
        material_processor: MaterialProcessor,
        carbon_processor: CarbonProcessor,
        compliance_checker: Compliance,
        logger: Logger,
    ):
        self.material_processor = material_processor
        self.carbon_processor = carbon_processor
        self.compliance_checker = compliance_checker
        self.logger = logger

    def analyze_elements(self, model: Any) -> None:
        """Processes all valid elements from the model."""
        for level, type_name, element in self._extract_valid_elements(model):
            try:
                self._process_materials(level, type_name, element)
            except Exception as e:
                self.logger.log_error(
                    object_id=getattr(element, ID, "Unknown"),
                    category="Processing Error",
                    message=f"Error processing element: {str(e)}",
                )

    def _extract_valid_elements(
        self, model: Any
    ) -> Generator[Tuple[str, str, Any], None, None]:
        """Yields valid elements (level, type_name, revit_object) after compliance checks."""
        for level, type_name, revit_object in self._get_element_hierarchy(model):
            if self._is_compliant(revit_object):
                yield level, type_name, revit_object
            else:
                self._log_skipped_element(revit_object)

    def _get_element_hierarchy(
        self, model: Any
    ) -> Generator[Tuple[str, str, Any], None, None]:
        """Flattens nested elements to yield (level, type_name, element)."""
        for level in self._get_elements(model, "model"):
            level_name = getattr(level, NAME, "Unknown")

            for type_group in self._get_elements(level, f"level {level_name}"):
                type_name = getattr(type_group, NAME, "Unknown")

                for group in self._get_elements(type_group, f"type {type_name}"):
                    yield from (
                        (level_name, type_name, revit_object)
                        for revit_object in self._get_elements(
                            group, f"group {getattr(group, NAME, 'Unknown')}"
                        )
                    )

    def _is_compliant(self, model_object: Any) -> bool:
        """Checks if an element passes compliance checks."""
        return self.compliance_checker.check_compliance(model_object)

    def _process_materials(self, level: str, type_name: str, model_object: Any) -> None:
        """Extracts material data and processes carbon calculations."""
        object_id = getattr(model_object, ID, "Unknown")
        material_quantities = model_object[PROPERTIES].get(MATERIAL_QUANTITIES, {})

        for material_name, material_data in material_quantities.items():
            processed_material = self.material_processor.process(
                object_id, material_data, level, type_name
            )
            if not processed_material:
                continue

            model_object[PROPERTIES]["Embodied Carbon Data"] = vars(processed_material)

            # Dictionary-based lookup instead of multiple if-elif checks
            category_map = {
                "floor": "Slabs",
                "stair": "Slabs",
                "slab edges": "Slabs",
                "wall": "Walls",
                "column": "Columns",
                "framing": "Beam",
                "beam": "Beam",
                "foundation": "Foundations",
            }
            category = next(
                (v for k, v in category_map.items() if k in type_name.lower()), None
            )

            if category and getattr(processed_material, "type") == "Concrete":
                model_object[PROPERTIES]["Embodied Carbon Data"]["element"] = category

            processed_carbon = self.carbon_processor.process(model_object)
            if processed_carbon:
                self.logger.log_success(
                    object_id=object_id,
                    category="Successfully Processed",
                    message="Carbon calculations completed successfully.",
                )
                model_object[PROPERTIES]["Embodied Carbon Calculations"] = vars(
                    processed_carbon
                )

    def _log_skipped_element(self, model_object: Any) -> None:
        """Logs elements that fail compliance checks."""
        self.logger.log_info(
            object_id=getattr(model_object, ID, "Unknown"),
            category="Skipped Elements",
            message="Element did not meet compliance criteria.",
        )

    @staticmethod
    def _get_elements(node: Any, context: str) -> list:
        """Get elements from a node, with consistent error handling."""
        elements = getattr(node, ELEMENTS, None)
        if not elements:
            name = getattr(node, NAME, "Unknown")
            raise ValueError(
                f"Invalid structure: missing elements in {context} '{name}'"
            )
        return elements
