from typing import Any
from src.interfaces.model_processor import ModelProcessor
from src.interfaces.material_processor import MaterialProcessor
from src.interfaces.compliance_checker import ComplianceChecker
from src.interfaces.logger import Logger
from src.utils.constants import (
    ELEMENTS,
    NAME,
    PROPERTIES,
    MATERIAL_QUANTITIES,
    ID,
    VOLUME,
    STRUCTURAL_ASSET,
    DENSITY,
)


class RevitModelProcessor(ModelProcessor):
    def __init__(
        self,
        material_processor: MaterialProcessor,
        compliance_checker: ComplianceChecker,
        logger: Logger,
    ):
        self._material_processor = material_processor
        self._compliance_checker = compliance_checker
        self._logger = logger

    def process_elements(self, model: Any) -> None:
        """Process all elements in the model hierarchically.
        Model → Levels → Type Groups → Elements"""
        levels = getattr(model, ELEMENTS, None)
        if not levels:
            raise ValueError("Invalid model: missing elements at root.")

        for level in levels:
            self._process_level(level)

    def _process_level(self, level: Any) -> None:
        """Process a single level in the model"""
        type_groups = getattr(level, ELEMENTS, None)
        if not type_groups:
            level_name = getattr(level, NAME, "Unknown")
            raise ValueError(
                f"Invalid level structure: missing elements in {level_name}"
            )

        level_name = getattr(level, NAME)
        for type_group in type_groups:
            self._process_type_group(type_group, level_name)

    def _process_type_group(self, type_group: Any, level_name: str) -> None:
        """Process a group of elements of the same type"""
        revit_objects = getattr(type_group, ELEMENTS, None)
        if not revit_objects:
            type_name = getattr(type_group, NAME, "Unknown")
            raise ValueError(f"Invalid type structure: missing elements in {type_name}")

        type_name = getattr(type_group, NAME)
        for revit_object in revit_objects:
            self.process_element(level_name, type_name, revit_object)

    def process_element(self, level: str, type_name: str, revit_object: Any) -> None:
        """Process a single element following original logic exactly"""
        element_id = getattr(revit_object, ID, None)
        if not element_id:
            return

        # First check elements
        elements = getattr(revit_object, ELEMENTS, None)
        if not elements:
            self._logger.log_warning(
                f"Missing elements", object_id=element_id, missing_property=ELEMENTS
            )
            return

        # Process each element
        for element in elements:
            # Check properties
            properties = getattr(element, PROPERTIES, None)
            if not properties:
                self._logger.log_warning(
                    f"Missing properties",
                    object_id=element_id,
                    missing_property=PROPERTIES,
                )
                return

            # Check Material Quantities
            material_quantities = properties.get(MATERIAL_QUANTITIES, None)
            if not material_quantities:
                self._logger.log_warning(
                    f"Missing Material Quantities",
                    object_id=element_id,
                    missing_property=MATERIAL_QUANTITIES,
                )
                return

            # Process each material
            for material_name, material_data in material_quantities.items():
                # Check required material properties
                for required_prop in [VOLUME, STRUCTURAL_ASSET, DENSITY]:
                    if required_prop not in material_data:
                        self._logger.log_warning(
                            f"Missing {required_prop}",
                            object_id=element_id,
                            missing_property=required_prop,
                        )
                        return

                try:
                    self._material_processor.process_material(
                        material_data, level, type_name
                    )
                except Exception as e:
                    self._logger.log_error(
                        f"Failed to process element {element_id}", error=str(e)
                    )
