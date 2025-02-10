from typing import Dict
from collections import defaultdict


# TODO: Replace with carbon aggregator when ready
class MassAggregator:
    """Cumulative sum of the computed masses. Grouped by level and type."""

    def __init__(self):
        self.totals = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    # TODO: Check! Changes for Revit model groups probably broke this
    def add_mass(
        self, mass: float, level: str, collection_type: str, material: str
    ) -> None:
        """Adds computed mass of a single object to the totals.
        Ignores computed masses < 1e-6.

        Args:
            mass (float): computed mass
            level (str): string of the associated level of the object
            collection_type (str): object collection (e.g. "Columns", "Structural Foundations")
            material (str): name of the structural asset
        """
        if mass <= 1e-6:
            return
        self.totals[level][collection_type][material] += mass

    # TODO: Check! Changes for Revit model groups probably broke this
    def get_totals(self) -> Dict:
        """Return computed totals in a structured dictionary.

        Returns:
            Dict: nested "by_level" and then "by_type"
        """
        return {
            "by_level": {
                level: {
                    "total": sum(
                        sum(material_masses.values())
                        for material_masses in types.values()
                    ),
                    "by_type": {
                        type_name: {
                            "total": sum(material_masses.values()),
                            "by_material": material_masses,
                        }
                        for type_name, material_masses in types.items()
                    },
                }
                for level, types in self.totals.items()
            },
        }
