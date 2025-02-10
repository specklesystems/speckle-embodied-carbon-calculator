from typing import Any
from src.core.base import Model
from src.core.base import Material
from src.core.base import Compliance
from src.core.base.logger import Logger
from src.applications.revit.utils.constants import (
    ELEMENTS,
    NAME,
    ID,
)

# NOTE: Only provide docstring if not covered by base class


class RevitModel(Model):
    """Implementation of the ModelProcessor in the Revit context."""

    def __init__(
        self,
        material_processor: Material,
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
        validation = self._compliance_checker.check_compliance(model_object, [])
        if not validation.is_valid:
            return

        try:
            # Process each material if element passed validation
            # TODO: Project 2427 is an interesting one with compound materials
            # TODO: Checkout object fefcc95c2f0ecd28a49ecdd7764e2d79. Worth skipping if volume = 0?
            for material_name, material_data in validation.material_quantities.items():
                self._material_processor.process_material(
                    material_data, level, type_name
                )
                # Log success only after all material processing complete
                self._logger.log_success(getattr(model_object, ID))

        except Exception as e:
            # Log any processing errors that occur
            self._logger.log_error(
                f"Failed to process element {getattr(model_object, ID)}", error=str(e)
            )

    # TODO: This is gross.
    def get_processing_results(self) -> tuple[list, dict]:
        return (
            self._logger.get_successful_summary(),
            self._logger.get_warnings_summary(),
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
