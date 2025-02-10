from typing import Any, List, Optional
from dataclasses import dataclass

from src.interfaces import ComplianceChecker, Logger
from src.utils.constants import (
    ID,
    SPECKLE_TYPE,
    LINE,
    ARC,
    CIRCLE,
    PROPERTIES,
    MATERIAL_QUANTITIES,
    STRUCTURAL_ASSET,
    VOLUME,
    DENSITY,
)


class RevitComplianceChecker(ComplianceChecker):
    """Implementation of the ComplianceChecker in the context of Revit.
    Checks if elements contain required properties for carbon calculations.
    """

    def __init__(self, logger: Logger):
        self._logger = logger

    def check_compliance(
        self, element: Any, required_properties: List[str]
    ) -> ComplianceChecker.ValidationResult:
        """
        Validates element and returns validation result with material data if valid.

        Args:
            element: Element to validate
            required_properties: List of required properties (unused but kept for interface)

        Returns:
            ValidationResult containing validation status and material data if valid
        """
        validation = self._validate_element(element)

        if not validation.is_valid:
            self._logger.log_warning(
                validation.error_message,
                object_id=getattr(element, ID, "unknown"),
                missing_property=validation.error_property,
            )

        return validation

    def _validate_element(self, element: Any) -> ComplianceChecker.ValidationResult:
        """Internal validation logic for a single element.

        Args:
            element: Element to validate

        Returns:
            ValidationResult with validation status and error details or material data
        """
        # Skip geometry elements
        speckle_type = getattr(element, SPECKLE_TYPE, None)
        if speckle_type in [LINE, ARC, CIRCLE]:
            return self.ValidationResult(
                is_valid=False, error_message="Geometry element - skipping"
            )

        # Check ID
        element_id = getattr(element, ID, None)
        if not element_id:
            return self.ValidationResult(
                is_valid=False, error_property=ID, error_message="Missing element ID"
            )

        # Check Properties
        properties = getattr(element, PROPERTIES, None)
        if not properties:
            return self.ValidationResult(
                is_valid=False,
                error_property=PROPERTIES,
                error_message="Missing Properties",
            )

        # Check Material Quantities
        material_quantities = properties.get(MATERIAL_QUANTITIES, None)
        if not material_quantities:
            return self.ValidationResult(
                is_valid=False,
                error_property=MATERIAL_QUANTITIES,
                error_message="Missing Material Quantities",
            )

        # Validate material properties
        for material_name, material_data in material_quantities.items():
            for required_prop in [VOLUME, STRUCTURAL_ASSET, DENSITY]:
                if required_prop not in material_data:
                    return self.ValidationResult(
                        is_valid=False,
                        error_property=required_prop,
                        error_message=f"Missing {required_prop}",
                    )

        return self.ValidationResult(
            is_valid=True, material_quantities=material_quantities
        )
