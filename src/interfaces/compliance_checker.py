from abc import ABC, abstractmethod
from typing import Any, List


class ComplianceChecker(ABC):
    @abstractmethod
    def check_compliance(self, element: Any, required_properties: List[str]) -> bool:
        """Check if element meets compliance requirements"""
        pass
