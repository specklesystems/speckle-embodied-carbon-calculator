from abc import ABC, abstractmethod
from typing import Any


class CarbonProcessor(ABC):
    """Interface for processing embodied carbon on an object."""

    @abstractmethod
    def process(
        self, modeL_object: Any
    ) -> None:
        """Compute embodied carbon per-element based previously asserted material properties.

        Args:
            model_object (Any): Model object to process
        """
        pass
