from abc import ABC, abstractmethod
from typing import Dict, Any


class MaterialProcessor(ABC):
    @abstractmethod
    def process_material(
        self, material_data: Dict[str, Any], level: str, type_name: str
    ) -> None:
        """Process material data and compute required properties"""
        pass
