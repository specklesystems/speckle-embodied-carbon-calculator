from abc import ABC, abstractmethod
from typing import Dict, Any


class MaterialProcessor(ABC):
    """Interface for processing a material."""

    @abstractmethod
    def process(
        self, object_id: str, material_data: Dict[str, Any], level: str, type_name: str
    ) -> None:
        """Process material data and compute required properties

        Args:
            object_id (str): Object ID
            material_data (Dict[str, Any]): material data
            level (str): associated level of object
            type_name (str): object type
        """
        pass
