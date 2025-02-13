from abc import ABC, abstractmethod
from typing import Any


class Compliance(ABC):
    """Interface for compliance checks.
    Compliance are intended to be called for every object where an attribute is assumed.
    """

    @abstractmethod
    def check_compliance(self, element: Any) -> bool:
        """Check if element contains attribute(s)"""
        pass
