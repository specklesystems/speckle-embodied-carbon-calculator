from src.core.base import CarbonProcessor
from src.core.types import MetalClass, WoodClass
from src.carbon.types import CarbonData
from src.carbon.data import wood_factors, metal_factors
from src.applications.revit.utils.material_type_handler import (
    MaterialType,
)
from src.applications.revit.utils.constants import (
    PROPERTIES,
)
import json


class RevitCarbonProcessor(CarbonProcessor):
    """Implementation of CarbonProcessor for Revit context."""

    def process(self, model_object) -> CarbonData:
        """Compute embodied carbon per-element based previously asserted material properties.

        Args:
            model_object (Any): Model object to process
        """
        material_type = model_object[PROPERTIES]["Embodied Carbon Data"]["type"]

        print(material_type)

        match material_type:
            case MaterialType.CONCRETE.value:
                # TODO
                pass
            case MaterialType.WOOD.value:
                # TODO
                pass
            case MaterialType.METAL.value:
                material_quantities = model_object[PROPERTIES]["Material Quantities"][
                    "FE_Steel"
                ]  # NOTE: This is dangerous.
                volume, density = (
                    material_quantities.volume.value,
                    material_quantities.density.value,
                )
                mass = volume * density

                # Default to hot rolled
                factor = metal_factors[MetalClass.HOT_ROLLED]

                embodied_carbon = mass * factor

                model_object[PROPERTIES]["Embodied Carbon Data"][
                    "category"
                ] = MetalClass.HOT_ROLLED
                model_object[PROPERTIES]["Embodied Carbon Data"][
                    "factor"
                ] = factor  # TODO: Append with units
                model_object[PROPERTIES]["Embodied Carbon Data"][
                    "embodied_carbon"
                ] = embodied_carbon  # TODO: Append with units
