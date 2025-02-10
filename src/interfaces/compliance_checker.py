from abc import ABC, abstractmethod
from typing import Any, List


# TODO: Passed around but never used
class ComplianceChecker(ABC):
    """Interface for compliance checks.
    Compliance are intended to be called for every object where an attribute is assumed.
    """
    # TODO: Passed around but never used
    @abstractmethod
    def check_compliance(self, element: Any, required_properties: List[str]) -> bool:
        """Check if element contains attribute(s)"""
        pass
