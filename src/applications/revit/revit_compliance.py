from typing import Any

from src.core.base import Compliance, Logger
from src.applications.revit.utils.constants import (
    ID,
    SPECKLE_TYPE,
    LINE,
    ARC,
    CIRCLE,
    PROPERTIES,
    MATERIAL_QUANTITIES,
    VOLUME,
    MATERIAL_CATEGORY,
    MATERIAL_CLASS,
    MATERIAL_NAME,
)


class RevitCompliance(Compliance):
    """Implementation of the ComplianceChecker in the context of Revit.
    Checks if elements contain required properties for carbon calculations.
    """

    def __init__(self, logger: Logger):
        self._logger = logger

    def check_compliance(self, element: Any) -> bool:
        """
        Validates element and returns validation result with material data if valid.

        Args:
            element: Element to validate

        Returns:
            ValidationResult containing validation status and material data if valid
        """

        # Check ID
        object_id = getattr(element, ID, None)
        if not object_id:
            raise ValueError("Should have an id.")

        # Skip geometry elements
        speckle_type = getattr(element, SPECKLE_TYPE, None)
        if speckle_type in [LINE, ARC, CIRCLE]:
            self._logger.log_info(
                object_id, "Skipped Geometry", "Skipped based on 'speckle_type'."
            )
            return False

        # Check Properties
        properties = getattr(element, PROPERTIES, None)
        if not properties:
            self._logger.log_error(
                object_id,
                "Missing 'properties'",
                "Valid object without a 'properties' " "attribute shouldn't happen.",
            )
            return False

        # Check Material Quantities
        material_quantities = properties.get(MATERIAL_QUANTITIES, None)
        if not material_quantities:
            self._logger.log_warning(
                object_id,
                "Missing 'Material Quantities'",
                "Absense of 'Material Quantities' " "indicates a non model-object.",
            )
            return False

        # Validate material properties
        # After discussions 11.02.2025, we're being forgiving on missing "Physical" (aka
        # StructuralAsset)
        for material_name, material_data in material_quantities.items():
            for required_prop in [
                VOLUME,
                MATERIAL_CATEGORY,
                MATERIAL_CLASS,
                MATERIAL_NAME,
            ]:
                if required_prop not in material_data:
                    self._logger.log_error(
                        object_id,
                        f"Missing {required_prop}.",
                        "Indicates changes to the Revit "
                        "connector. Inspect commit and "
                        "update accordingly.",
                    )
                    return False

        return True
