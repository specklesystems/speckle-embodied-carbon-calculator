from abc import ABC, abstractmethod
from typing import Any


class Model(ABC):
    """Interface for model processing."""

    @abstractmethod
    def process_elements(self, model: Any) -> None:
        """Process all elements in the model.

        Args:
            model (Any): root commit
        """
        pass

    # TODO: element should be Base?
    @abstractmethod
    def process_element(self, level: str, type_name: str, model_object: Any) -> None:
        """Process a single element.

        Args:
            level (str): associated level of object
            type_name (str): object type
            model_object (Any): speckle object
        """
        pass

    # TODO: This is gross
    @abstractmethod
    def get_processing_results(self) -> tuple[list, dict]:
        """Expose logging results."""
        pass
