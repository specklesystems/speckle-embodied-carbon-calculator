from typing import Dict, Any, Protocol

from src.core.base import Logger
from src.core.types.material_data import MaterialData
from src.applications.revit.utils.material_type_handler import (
    MaterialType,
    ConcreteHandler,
    MetalHandler,
    WoodHandler,
)
from src.applications.revit.utils.constants import (
    MATERIAL_TYPE,
    MATERIAL_NAME,
)


class MaterialQualityStrategy(Protocol):
    """Protocol defining how to process materials of different quality levels"""

    def process(
        self,
        object_id: str,
        material_data: Dict[str, Any],
        volume: float,
        logger: Logger,
    ) -> MaterialData:
        ...


class HighQualityStrategy(MaterialQualityStrategy):
    """Strategy for processing high-quality materials (with structural asset)"""

    def __init__(self):
        self._handlers = {
            MaterialType.CONCRETE.value: ConcreteHandler(),
            MaterialType.METAL.value: MetalHandler(),
            MaterialType.WOOD.value: WoodHandler(),
        }

    def process(
        self,
        object_id: str,
        material_data: Dict[str, Any],
        volume: float,
        logger: Logger,
    ) -> MaterialData:
        if MATERIAL_TYPE not in material_data:
            raise ValueError("Missing material type")  # Rather safe than sorry

        material_type = material_data[MATERIAL_TYPE]
        handler = self._handlers.get(material_type)
        if not handler:
            raise ValueError(f"Unsupported material type: {material_type}")

        try:
            result = handler.create_material_data(material_data, volume)
            logger.log_success(
                object_id,
                "High-Quality Material Definitions",
                "Contains all expected attributes.",
            )
            return result
        except Exception as e:
            raise Exception(f"Failed to process material: {str(e)}")


class LowQualityStrategy(MaterialQualityStrategy):
    """Strategy for processing low-quality materials (without structural asset)"""

    DEFAULT_CONCRETE_GRADE = "35"
    DEFAULT_STEEL_DENSITY = 7851.81483993

    def process(
        self,
        object_id: str,
        material_data: Dict[str, Any],
        volume: float,
        logger: Logger,
    ) -> MaterialData:
        material_name = material_data[MATERIAL_NAME].lower()

        if "clt" in material_name:
            logger.log_warning(
                object_id,
                "Low-Quality Wood Material Definitions",
                "Wood has no structural asset and found base on string search",
            )
            return MaterialData(MaterialType.WOOD.value, volume)
        elif "concrete" in material_name:
            logger.log_warning(
                object_id,
                "Low-Quality Concrete Material Definitions",
                "Concrete has no structural asset and found based on string search",
            )
            return MaterialData(
                MaterialType.CONCRETE.value, volume, grade=self.DEFAULT_CONCRETE_GRADE
            )
        elif "steel" in material_name:
            logger.log_warning(
                object_id,
                "Low-Quality Steel Material Definitions",
                "Steel has no structural asset and found based on string search",
            )
            return MaterialData(
                MaterialType.METAL.value,
                volume,
                density=self.DEFAULT_STEEL_DENSITY,
                mass=volume * self.DEFAULT_STEEL_DENSITY,
            )
        else:
            raise ValueError(
                f"Unable to determine material type from name: {material_name}"
            )
