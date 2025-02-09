from typing import Dict, Any

from src.aggregators.carbon_totals import MassAggregator
from src.logging.compliance_logger import ComplianceLogger
from src.utils.constants import *  # wildcard is a little dangerous


class CommitProcessor:
    def __init__(self):
        self.logger = ComplianceLogger()
        self.mass_aggregator = MassAggregator()

    def process_elements(
        self, model: "Base"
    ) -> None:  # No return needed, we're modifying in-place
        levels = getattr(model, ELEMENTS, None)
        if not levels:  # First nesting => levels
            raise ValueError("Invalid commit: missing elements at the model root.")

        for level in levels:
            type_groups = getattr(level, ELEMENTS, None)
            if not type_groups:
                raise ValueError(
                    f"Invalid level structure: missing elements in {getattr(level,NAME, '!Missing name attribute!')}"
                )

            for type_group in type_groups:
                revit_objects = getattr(type_group, ELEMENTS, None)
                if not revit_objects:
                    raise ValueError(
                        f"Invalid type structure: missing elements in "
                        f"{getattr(type_group, NAME, '!Missing name attribute!')}"
                    )

                level_name = getattr(level, NAME, None)
                type_name = getattr(type_group, NAME, None)
                if level_name is None or type_name is None:
                    raise ValueError(
                        f"Every object should be on a level and be of a type."
                    )

                for revit_object in revit_objects:
                    self.process_element(
                        level=level_name, type_name=type_name, revit_object=revit_object
                    )

    def process_element(
        self, level: str, type_name: str, revit_object: Dict[str, Any]
    ) -> None:  # Mutating in-place
        elements = getattr(revit_object, ELEMENTS, None)
        if not elements:
            self.logger.log_missing_properties(revit_object[ID], ELEMENTS)

        for element in elements:
            properties = getattr(element, PROPERTIES, None)
            if not properties:
                self.logger.log_missing_properties(
                    revit_object[ID], PROPERTIES
                )  # 🤔 revit_object/element?
                return

            material_quantities = properties.get(MATERIAL_QUANTITIES, None)
            if not material_quantities:
                self.logger.log_missing_properties(
                    revit_object[ID], MATERIAL_QUANTITIES
                )
                return

            for material_name, material_data in material_quantities.items():
                if VOLUME not in material_data:
                    self.logger.log_missing_properties(revit_object[ID], VOLUME)
                    return

                if STRUCTURAL_ASSET not in material_data:
                    self.logger.log_missing_properties(
                        revit_object[ID], STRUCTURAL_ASSET
                    )
                    return

                # ⚠️ This should never hit. No STRUCTURAL_ASSET → no DENSITY
                if DENSITY not in material_data:
                    self.logger.log_missing_properties(revit_object[ID], DENSITY)
                    return

                try:
                    # Dict structure for numerical properties(e.g.)
                    # {"name" : "volume", "value" : 100, "units" : "Cubic metres"}
                    # 🤫 Shouldn't change.
                    volume = material_data[VOLUME][VALUE]
                    density = material_data[DENSITY][VALUE]
                    mass = volume * density

                    material_data[MASS] = {
                        NAME: MASS,
                        VALUE: mass,
                        UNITS: material_data[DENSITY][UNITS].split()[0],
                        # TODO: 🫣 Units string operation is super sketchy.
                    }

                    self.mass_aggregator.add_mass(
                        mass, level, type_name, material_data[STRUCTURAL_ASSET]
                    )

                # ❗ We've validated everything. If the computation fails, there's a bug.
                # 🤾 Throw.
                except (ValueError, TypeError, KeyError) as e:
                    raise ValueError(
                        f"Computation failed for {material_name} despite having required properties: {str(e)}"
                    ) from e
