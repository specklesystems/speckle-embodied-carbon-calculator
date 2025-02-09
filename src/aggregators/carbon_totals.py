from typing import Dict
from collections import defaultdict


class MassAggregator:
    def __init__(self):
        self.totals = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    def add_mass(self, mass: float, level: str, type: str, material: str) -> None:
        if mass <= 1e-6:
            return
        self.totals[level][type][material] += mass

    def get_totals(self) -> Dict:
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
