from typing import Any, Tuple, Dict, List
from src.core.base import Model
from src.core.base import MaterialProcessor
from src.core.base import Compliance
from src.core.base.logger import Logger
from src.applications.revit.utils.constants import (
    ELEMENTS,
    NAME,
    ID,
    MATERIAL_QUANTITIES,
    PROPERTIES,
)

# NOTE: Only provide docstring if not covered by base class


class RevitModel(Model):
    """Implementation of the ModelProcessor in the Revit context."""

    def __init__(
        self,
        material_processor: MaterialProcessor,
        compliance_checker: Compliance,
        logger: Logger,
    ):
        self._material_processor = material_processor
        self._compliance_checker = compliance_checker
        self._logger = logger

    def process_elements(self, model: Any) -> None:
        """Model traversal.
        Model → Levels → Type Groups → Elements.

        Performance Notes:
            - Threading? Could be cool, but:
                - Profile code first. Do we need it?
                - Not really I/O bound. Our traversal is just walking through an in-memory object structure
                - TBH I'm scared of the hierarchy
                - Thread safety? Shared loggers and aggregators.
            - Flattening nested iterations?
                - Code less readable (e.g. chain.from_iterable(..))
                - Obscures hierarchical nature of data
                - Performance benefit(s) minimal?
                - Harder to debug
        """
        levels = self._get_elements(model, "model")

        for level in levels:
            level_name = self._get_name(level)
            type_groups = self._get_elements(level, f"level {level_name}")

            for type_group in type_groups:
                type_name = self._get_name(type_group)
                groups = self._get_elements(type_group, f"type {type_name}")

                for group in groups:
                    revit_objects = self._get_elements(
                        group, f"group {self._get_name(group)}"
                    )
                    for revit_object in revit_objects:
                        self.process_element(level_name, type_name, revit_object)

    def process_element(self, level: str, type_name: str, model_object: Any) -> None:
        """Process a single model element if it passes compliance checks.

        Args:
            level (str): associated level of the object
            type_name (str): family / type of the object
            model_object (Any): speckle object containing properties for processing
        """
        # First check compliance - this also handles logging any validation warnings
        valid = self._compliance_checker.check_compliance(model_object)
        if not valid:
            return

        # These are now safe to do after compliance checking
        material_quantities = model_object[PROPERTIES][MATERIAL_QUANTITIES]
        object_id = getattr(model_object, ID)

        try:
            # Process each material if element passed validation
            for material_name, material_data in material_quantities.items():
                processed_material = self._material_processor.process(
                    object_id, material_data, level, type_name
                )
                if processed_material:  # If processing was successful
                    self._logger.log_success(
                        object_id=object_id,
                        category="Successfully Processed",
                        message="Carbon calculations completed successfully for this element.",
                    )

                    model_object[PROPERTIES]["Embodied Carbon Data"] = vars(
                        processed_material
                    )

                    if getattr(processed_material, "type") == "Concrete":
                        model_object[PROPERTIES]["Embodied Carbon Data"][
                            "element"
                        ] = self._categorize(type_name)

        except Exception as e:
            # Log any processing errors that occur
            self._logger.log_error(object_id, "Material Processing Error", str(e))

    def get_processing_results(
        self,
    ) -> Tuple[
        Dict[str, List[str]],
        Dict[str, List[str]],
        Dict[str, List[str]],
        Dict[str, List[str]],
    ]:
        """Get processing results in the format expected by main.py.

        Returns:
            Tuple containing:
            - Dict mapping success categories to lists of successfully processed object IDs
            - Dict mapping information categories to lists of affected object IDs
            - Dict mapping warning categories to lists of affected object IDs
            - Dict mapping error categories to lists of affected object IDs
        """
        return (
            self._logger.get_success_summary(),
            self._logger.get_info_summary(),
            self._logger.get_warnings_summary(),
            self._logger.get_errors_summary(),
        )

    @staticmethod
    def _get_elements(node: Any, context: str) -> list:
        """Get elements from a node, with consistent error handling.

        Args:
            node: Node to extract elements from
            context: Context for error message if elements missing

        Raises:
            ValueError: If elements are missing
        """
        elements = getattr(node, ELEMENTS, None)
        if not elements:
            name = getattr(node, NAME, "Unknown")
            raise ValueError(
                f"Invalid structure: missing elements in {context} '{name}'"
            )
        return elements

    @staticmethod
    def _get_name(node: Any) -> str:
        """Safely get name from node, with fallback"""
        return getattr(node, NAME, "Unknown")

    @staticmethod
    def _categorize(type_name: str) -> str:
        searchable_string = type_name.lower()
        if (
            "floor" in searchable_string
            or "stair" in searchable_string
            or "slab edges" in searchable_string
        ):
            return "Slabs"
        elif "wall" in searchable_string:
            return "Walls"
        elif "column" in searchable_string:
            return "Columns"
        elif "framing" in searchable_string or "beam" in searchable_string:
            return "Beam"
        elif "foundation" in searchable_string:
            return "Foundations"
        else:
            raise ValueError(f"{type_name} not accounted for.")
