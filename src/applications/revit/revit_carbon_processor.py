from src.core.base import CarbonProcessor
from src.carbon.types import CarbonData
from src.applications.revit.utils.material_type_handler import (
    MaterialType,
)
from src.applications.revit.utils.constants import (
    PROPERTIES,
)

class RevitCarbonProcessor(CarbonProcessor):
    """Implementation of CarbonProcessor for Revit context."""

    def process(
        self, model_object
    ) -> CarbonData:
        """Compute embodied carbon per-element based previously asserted material properties.

        Args:
            model_object (Any): Model object to process
        """
        material_type = model_object[PROPERTIES]["Embodied Carbon Data"]["type"]

        print(material_type)

        match material_type:
            case MaterialType.CONCRETE:
                # TODO
                pass
            case MaterialType.WOOD:
                # TODO
                pass
            case MaterialType.METAL:
                # TODO
                pass
