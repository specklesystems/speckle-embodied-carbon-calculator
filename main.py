from collections import defaultdict

from pydantic import Field
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)

from typing import Dict, Generator, Any, List

from src.domain.carbon.databases.enums import (
    SteelDatabase,
    TimberDatabase,
    ConcreteDatabase,
)
from src.domain.types import BuildingElement
from src.infrastructure.logging import Logging
from src.services.carbon_calculator import CarbonCalculator
from src.services.element_processor import ElementProcessor
from src.services.material_processor import MaterialProcessor


def create_one_of_enum(enum_cls):
    """
    Helper function to create a JSON schema from an Enum class.
    This is used for generating user input forms in the UI.
    """
    return [{"const": item.value, "title": item.name} for item in enum_cls]


class FunctionInputs(AutomateBase):
    """User-defined function inputs."""

    steel_database: str = Field(
        default=SteelDatabase.Type350MPa,
        title="Steel Database",
        description="Database used for the GWP of steel objects",
        json_schema_extra={"oneOf": create_one_of_enum(SteelDatabase)},
    )

    timber_database: str = Field(
        default=TimberDatabase.Binderholz2019,
        title="Timber Database",
        description="Database used for the GWP of timber objects",
        json_schema_extra={"oneOf": create_one_of_enum(TimberDatabase)},
    )

    concrete_database: str = Field(
        default=ConcreteDatabase.GulLowAir.value,
        title="Concrete Database",
        description="Database used for the GWP of concrete objects",
        json_schema_extra={"oneOf": create_one_of_enum(ConcreteDatabase)},
    )

    country: str = Field(
        default="CAN",
        title="Country",
        description="Country for concrete strength units (CAN: MPa, USA: PSI)",
        json_schema_extra={
            "oneOf": [
                {"const": "CAN", "title": "Canada (MPa)"},
                {"const": "USA", "title": "United States (PSI)"},
            ]
        },
    )

    # Add reinforcement rates based on Image 1
    reinforcement_grade_beam: float = Field(
        default=100.0,
        title="Grade Beam Reinforcement (kg/m³)",
    )

    reinforcement_slab_on_grade: float = Field(
        default=85.0,
        title="Slab on Grade Reinforcement (kg/m³)",
    )

    reinforcement_pad_footing: float = Field(
        default=100.0,
        title="Pad Footing Reinforcement (kg/m³)",
    )

    reinforcement_pile: float = Field(
        default=100.0,
        title="Pile Reinforcement (kg/m³)",
    )

    reinforcement_strip_footing: float = Field(
        default=100.0,
        title="Strip Footing Reinforcement (kg/m³)",
    )

    reinforcement_pile_cap: float = Field(
        default=100.0,
        title="Pile Cap Reinforcement (kg/m³)",
    )

    reinforcement_gravity_wall: float = Field(
        default=150.0,
        title="Gravity Wall Reinforcement (kg/m³)",
    )

    reinforcement_column: float = Field(
        default=450.0,
        title="Column Reinforcement (kg/m³)",
    )

    reinforcement_shear_wall: float = Field(
        default=150.0,
        title="Shear Wall Reinforcement (kg/m³)",
    )

    reinforcement_concrete_slab: float = Field(
        default=120.0,
        title="Concrete Slab Reinforcement (kg/m³)",
    )

    reinforcement_beam: float = Field(
        default=220.0,
        title="Beam Reinforcement (kg/m³)",
    )

    reinforcement_topping_slab: float = Field(
        default=85.0,
        title="Topping Slab Reinforcement (kg/m³)",
    )


class RevitCarbonAnalyzer:
    """Main application for analyzing carbon in Revit models."""

    def __init__(
        self,
        material_processor: MaterialProcessor,
        element_processor: ElementProcessor,
        carbon_calculator: CarbonCalculator,
        logger: Logging,
    ):
        """
        Initialize with injected dependencies.

        Args:
            material_processor: Service for processing raw materials
            element_processor: Service for processing Revit elements
            carbon_calculator: Service for calculating carbon emissions
            logger: Logging service
        """
        self.material_processor = material_processor
        self.element_processor = element_processor
        self.carbon_calculator = carbon_calculator
        self.logger = logger

    def analyze_model(self, model_root) -> dict:
        """Analyze a Revit model for carbon emissions."""
        results = {
            "processed_elements": [],
            "skipped_elements": [],
            "warning_elements": [],  # For invalid elements
            "errors": [],
            "total_carbon": 0.0,
            "missing_factors": {"timber": [], "steel": [], "concrete": []},
        }

        # Process each element
        for element in self._iterate_elements(model_root):
            try:
                element_result = self._process_single_element(element)
                if element_result["status"] == "processed":
                    results["processed_elements"].append(element_result)
                    results["total_carbon"] += element_result["total_carbon"]
                elif element_result["status"] == "skipped":
                    results["skipped_elements"].append(element_result)
                elif element_result["status"] == "warning":
                    results["warning_elements"].append(element_result)
                else:
                    results["errors"].append(element_result)
            except Exception as e:
                results["errors"].append(
                    {
                        "id": getattr(element, "id", "unknown"),
                        "error": str(e),
                        "status": "error",
                    }
                )

            # Get missing factors
        (
            missing_timber,
            missing_steel,
            missing_concrete,
        ) = self.carbon_calculator.get_missing_factors()
        results["missing_factors"]["timber"] = missing_timber
        results["missing_factors"]["steel"] = missing_steel
        results["missing_factors"]["concrete"] = missing_concrete

        # Log missing factors
        if missing_timber:
            print(f"Missing timber factors ({len(missing_timber)}):")
            for item in missing_timber:
                print(f"  - {item}")

        if missing_steel:
            print(f"Missing steel factors ({len(missing_steel)}):")
            for item in missing_steel:
                print(f"  - {item}")

        if missing_concrete:
            print(f"Missing concrete factors ({len(missing_concrete)}):")
            for item in missing_concrete:
                print(f"  - {item}")

        return results

    def _process_single_element(self, element: Dict) -> Dict:
        """Process a single element and return its results."""
        element_id = getattr(element, "id", "unknown")

        # Check if this element should be skipped
        if self.element_processor.is_skipped(element):
            return {
                "id": element_id,
                "status": "skipped",
                "reason": "Element type or family in skip list",
            }

        # Check if element is valid - mark as warning if not
        if not self.element_processor.is_valid_element(element):
            return {
                "id": element_id,
                "status": "warning",
                "reason": "Missing required properties",
            }

        # Process element
        processed_element = self.element_processor.process_element(element)
        if not processed_element:
            return {
                "id": element_id,
                "status": "error",
                "reason": "Element processing failed",
            }

        # Calculate carbon
        try:
            carbon_results = self.carbon_calculator.calculate_carbon(processed_element)

            # Initialize Embodied Carbon Calculation dictionary
            embodied_carbon_data = {}

            for material_name, result in carbon_results.items():
                # Create a dictionary for each material instead of an array
                material_data = {}

                if result.category == "Wood":
                    # For timber - use name/value/units format as dictionary entries
                    material_data = {
                        "volume": {
                            "name": "volume",
                            "value": result.quantity,
                            "units": "m³",
                        },
                        "database": {
                            "name": "database",
                            "value": result.database,
                            "units": None,
                        },
                        "ecf": {
                            "name": "ecf",
                            "value": result.factor,
                            "units": "kgCO₂e/m³",
                        },
                        "embodied carbon": {
                            "name": "embodied carbon",
                            "value": result.total_carbon,
                            "units": "kgCO₂e",
                        },
                    }
                elif result.category == "Concrete":
                    # For concrete (include both concrete and reinforcement)
                    material_data = {
                        "volume": {
                            "name": "volume",
                            "value": result.concrete_volume,
                            "units": "m³",
                        },
                        "database": {
                            "name": "database",
                            "value": result.database,
                            "units": None,
                        },
                        "ecf": {
                            "name": "ecf",
                            "value": result.factor,
                            "units": "kgCO₂e/m³",
                        },
                        "concrete carbon": {
                            "name": "concrete carbon",
                            "value": result.concrete_carbon,
                            "units": "kgCO₂e",
                        },
                        "reinforcement mass": {
                            "name": "reinforcement mass",
                            "value": result.reinforcement_mass,
                            "units": "kg",
                        },
                        "reinforcement rate": {
                            "name": "reinforcement rate",
                            "value": result.reinforcement_rate,
                            "units": "kg/m³",
                        },
                        "reinforcement ecf": {
                            "name": "reinforcement ecf",
                            "value": result.reinforcement_factor,
                            "units": "kgCO₂e/kg",
                        },
                        "reinforcement carbon": {
                            "name": "reinforcement carbon",
                            "value": result.reinforcement_carbon,
                            "units": "kgCO₂e",
                        },
                        "embodied carbon": {
                            "name": "embodied carbon",
                            "value": result.total_carbon,
                            "units": "kgCO₂e",
                        },
                    }
                elif result.category == "Metal":
                    # For metal
                    material_data = {
                        "mass": {
                            "name": "mass",
                            "value": result.quantity,
                            "units": "kg",
                        },
                        "database": {
                            "name": "database",
                            "value": result.database,
                            "units": None,
                        },
                        "ecf": {
                            "name": "ecf",
                            "value": result.factor,
                            "units": "kgCO₂e/kg",
                        },
                        "embodied carbon": {
                            "name": "embodied carbon",
                            "value": result.total_carbon,
                            "units": "kgCO₂e",
                        },
                    }

                # Add this material's data to the main dictionary
                embodied_carbon_data[material_name] = material_data

            # Attach the data to the original element
            if hasattr(element, "properties"):
                element.properties["Embodied Carbon Calculation"] = embodied_carbon_data

            return {
                "id": element_id,
                "status": "processed",
                "level": processed_element.level,
                "category": processed_element.category,
                "materials": [
                    {
                        "name": m.properties.name,
                        "type": m.type.value,
                        "volume": m.properties.volume,
                    }
                    for m in processed_element.materials
                ],
                "carbon_results": carbon_results,
                "total_carbon": sum(r.total_carbon for r in carbon_results.values()),
            }
        except Exception as e:
            return {
                "id": element_id,
                "status": "error",
                "error": f"Carbon calculation failed: {str(e)}",
            }

    @staticmethod
    def _iterate_elements(model_data) -> Generator[Dict, None, None]:
        """Iterate through all elements in the model."""
        for level in getattr(model_data, "elements", []):
            for type_group in getattr(level, "elements", []):
                for element_group in getattr(type_group, "elements", []):
                    for element in getattr(element_group, "elements", []):
                        yield element


def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:
    """Program entry point."""
    try:
        # Get string values from enums if needed
        steel_db = function_inputs.steel_database
        timber_db = function_inputs.timber_database
        concrete_db = function_inputs.concrete_database
        country = function_inputs.country

        # Ensure we're working with string values, not enum objects
        if hasattr(steel_db, "value"):
            steel_db = steel_db.value
        if hasattr(timber_db, "value"):
            timber_db = timber_db.value
        if hasattr(concrete_db, "value"):
            concrete_db = concrete_db.value
        # Create custom reinforcement rates dictionary
        custom_reinforcement_rates = {
            "Grade Beam": function_inputs.reinforcement_grade_beam,
            "Slab on Grade": function_inputs.reinforcement_slab_on_grade,
            "Pad Footing": function_inputs.reinforcement_pad_footing,
            "Pile": function_inputs.reinforcement_pile,
            "Strip Footing": function_inputs.reinforcement_strip_footing,
            "Pile Cap": function_inputs.reinforcement_pile_cap,
            "Walls - wind/gravity": function_inputs.reinforcement_gravity_wall,
            "Column": function_inputs.reinforcement_column,
            "Shear Walls": function_inputs.reinforcement_shear_wall,
            "Concrete Slabs": function_inputs.reinforcement_concrete_slab,
            "Beams": function_inputs.reinforcement_beam,
            "Topping Slabs": function_inputs.reinforcement_topping_slab,
        }

        # Create dependencies with proper DI
        logger = Logging()
        material_processor = MaterialProcessor()
        element_processor = ElementProcessor(
            material_processor=material_processor, logger=logger
        )
        carbon_calculator = CarbonCalculator(
            steel_database=steel_db,
            timber_database=timber_db,
            concrete_database=concrete_db,
            country=country,
            custom_reinforcement_rates=custom_reinforcement_rates,
        )

        # Initialize analyzer with injected dependencies
        analyzer = RevitCarbonAnalyzer(
            material_processor=material_processor,
            element_processor=element_processor,
            carbon_calculator=carbon_calculator,
            logger=logger,
        )

        # Get commit root
        version_id = automate_context.automation_run_data.triggers[0].payload.version_id
        commit_root = automate_context.speckle_client.commit.get(
            automate_context.automation_run_data.project_id, version_id
        )

        # Get model root
        model_root = automate_context.receive_version()

        # Validate Revit source
        if not _validate_revit_source(commit_root):
            automate_context.mark_run_failed("Model must be from Revit")
            return

        # Run analysis - convert Speckle model to dict for processing
        results = analyzer.analyze_model(model_root)

        # Process results
        _process_automation_results(automate_context, results)

        # Calculate success percentage (successful / (successful + errors))
        total_processed = (
            len(results["processed_elements"])
            + len(results["errors"])
            + len(results["warning_elements"])
        )
        success_percentage = (
            (len(results["processed_elements"]) / total_processed * 100)
            if total_processed > 0
            else 100
        )

        # Prepare detailed success message
        success_message = (
            f"🚀 Analysis complete.\n\n"
            f"\tProcessed:\t\t{results['success_count']} elements\n"
            f"\tSkipped:\t\t\t{results['skipped_count']} elements\n"
            f"\tWarnings:\t\t{results['warning_count']} elements\n"
            f"\tErrors:\t\t\t\t{results['error_count']} elements\n"
            f"\tSuccess rate:\t{success_percentage:.1f}%\n\n"
            f"\tTotal carbon:\t{results['total_carbon']:.0f} kgCO₂e\n"
        )

        # Add missing factors to message if any
        missing_timber = results["missing_factors"]["timber"]
        missing_steel = results["missing_factors"]["steel"]

        if missing_timber or missing_steel:
            success_message += "\nMissing emission factors detected:\n"

            if missing_timber:
                success_message += (
                    f"- Timber ({len(missing_timber)}): {', '.join(missing_timber[:5])}"
                )
                if len(missing_timber) > 5:
                    success_message += f" and {len(missing_timber) - 5} more"
                success_message += "\n"

            if missing_steel:
                success_message += (
                    f"- Steel ({len(missing_steel)}): {', '.join(missing_steel[:5])}"
                )
                if len(missing_steel) > 5:
                    success_message += f" and {len(missing_steel) - 5} more"
                success_message += "\n"

            success_message += "\nThese materials were assigned zero carbon. Consider updating the database."

        else:
            success_message += (
                "\nNOTE: All materials successfully matched with emission factors."
            )

        # Upload mutated model
        # automate_context.create_new_version_in_project(
        #    model_root, f"{commit_root.branchName}_embodied_carbon"
        # )

        # Mark success with detailed message
        automate_context.mark_run_success(success_message)

    except Exception as e:
        automate_context.mark_run_failed(f"Analysis failed: {str(e)}")
        raise


def _validate_revit_source(commit_root: Any) -> bool:
    """Validate that the model is from Revit."""
    source_app = getattr(commit_root, "sourceApplication", "").lower()
    return source_app.startswith("revit")


def _process_automation_results(
    automate_context: AutomationContext, results: dict
) -> None:
    """Process results and attach them to the automation context."""
    # Process each category and attach to objects

    # Successes
    if results["processed_elements"]:
        automate_context.attach_success_to_objects(
            category="Carbon Analysis",
            object_ids=[e["id"] for e in results["processed_elements"]],
            message="Carbon calculations completed successfully for these elements!",
        )

    # Skipped elements (info)
    if results["skipped_elements"]:
        automate_context.attach_info_to_objects(
            category="Skipped Elements",
            object_ids=[e["id"] for e in results["skipped_elements"]],
            message="Elements that were intentionally skipped.",
        )

    # Warnings
    if results["warning_elements"]:
        automate_context.attach_warning_to_objects(
            category="Missing Material Data",
            object_ids=[e["id"] for e in results["warning_elements"]],
            message="Elements missing material data required for carbon calculation.",
        )

    # Errors
    if results["errors"]:
        automate_context.attach_error_to_objects(
            category="Processing Errors",
            object_ids=[e["id"] for e in results["errors"]],
            message="Failure processing the following elements.",
        )

    # Add statistics to results for use in success message
    results["success_count"] = len(results["processed_elements"])
    results["warning_count"] = len(results["warning_elements"])
    results["skipped_count"] = len(results["skipped_elements"])
    results["error_count"] = len(results["errors"])


if __name__ == "__main__":
    execute_automate_function(automate_function, FunctionInputs)
