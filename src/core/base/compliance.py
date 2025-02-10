from abc import ABC, abstractmethod
from typing import Any, List
from dataclasses import dataclass
from typing import Optional


class Compliance(ABC):
    """Interface for compliance checks.
    Compliance are intended to be called for every object where an attribute is assumed.
    """

    @dataclass
    class ValidationResult:
        """Results of element validation including material data if valid"""

        is_valid: bool
        material_quantities: Optional[dict] = None
        error_property: Optional[str] = None
        error_message: Optional[str] = None

    @abstractmethod
    def check_compliance(
        self, element: Any, required_properties: List[str]
    ) -> ValidationResult:
        """Check if element contains attribute(s)"""
        pass
