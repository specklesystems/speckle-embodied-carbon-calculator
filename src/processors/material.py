from typing import Dict, Any
from src.interfaces.material_processor import MaterialProcessor
from src.models.material import (
    MaterialData,
)  # Import from models instead of defining here
from src.utils.constants import *


class RevitMaterialProcessor(MaterialProcessor):
    def __init__(self, mass_aggregator: "MassAggregator"):
        self._mass_aggregator = mass_aggregator

    def process_material(
        self, material_data: Dict[str, Any], level: str, type_name: str
    ) -> MaterialData:
        volume = material_data[VOLUME][VALUE]
        density = material_data[DENSITY][VALUE]
        mass = volume * density
        structural_asset = material_data[STRUCTURAL_ASSET]

        mat_data = MaterialData(
            volume=volume, density=density, structural_asset=structural_asset, mass=mass
        )

        self._mass_aggregator.add_mass(mass, level, type_name, structural_asset)
        return mat_data
