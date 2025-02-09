from abc import ABC, abstractmethod
from typing import Any


class ModelProcessor(ABC):
    @abstractmethod
    def process_elements(self, model: Any) -> None:
        """Process all elements in the model"""
        pass

    @abstractmethod
    def process_element(self, level: str, type_name: str, element: Any) -> None:
        """Process a single element"""
        pass
