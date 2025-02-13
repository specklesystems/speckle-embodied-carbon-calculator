from typing import Dict, Any
from src.core.base.logger import Logger
from src.applications.revit.utils.material_quality_strategy import (
    HighQualityStrategy,
    LowQualityStrategy,
)
from src.core.base import MaterialProcessor
from src.core.types.material_data import (
    MaterialData,
)
from src.applications.revit.utils.constants import (
    VOLUME,
    VALUE,
    STRUCTURAL_ASSET,
)


class RevitMaterialProcessor(MaterialProcessor):
    """Implementation of the MaterialProcessor for the Revit context."""

    def __init__(self, mass_aggregator: "MassAggregator", logger: Logger):
        self._mass_aggregator = mass_aggregator
        self._logger = logger
        self._high_quality_strategy = HighQualityStrategy()
        self._low_quality_strategy = LowQualityStrategy()

    def process(
        self, object_id: str, material_data: Dict[str, Any], level: str, type_name: str
    ) -> MaterialData:
        # Volume has already been checked for
        volume = material_data[VOLUME][VALUE]

        try:
            if STRUCTURAL_ASSET in material_data:
                return self._high_quality_strategy.process(
                    object_id, material_data, volume, self._logger
                )
            else:
                return self._low_quality_strategy.process(
                    object_id, material_data, volume, self._logger
                )
        except Exception as e:
            raise ValueError(str(e))
