from collections import defaultdict

from pydantic import Field
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)

from typing import Dict, Generator, Any, List

from src.domain.carbon.databases.enums import SteelDatabase, TimberDatabase
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
        default=ConcreteDatabase.GUL_LOW_AIR.value,
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

    def __init__(self, steel_database: str, timber_database: str):
        self.material_processor = MaterialProcessor()
        self.element_processor = ElementProcessor(
            material_processor=self.material_processor, logger=Logging()
        )
        self.carbon_calculator = CarbonCalculator(
            steel_database=steel_database.value
            if isinstance(steel_database, SteelDatabase)
            else steel_database,
            timber_database=timber_database.value
            if isinstance(timber_database, SteelDatabase)
            else timber_database,
        )

    def analyze_model(self, model_root) -> dict:
        """Analyze a Revit model for carbon emissions."""
        results = {
            "processed_elements": [],
            "skipped_elements": [],
            "errors": [],
            "total_carbon": 0.0,
            "missing_factors": {"timber": [], "steel": []},
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
        missing_timber, missing_steel = self.carbon_calculator.get_missing_factors()
        results["missing_factors"]["timber"] = missing_timber
        results["missing_factors"]["steel"] = missing_steel

        # Log missing factors
        if missing_timber:
            print(f"Missing timber factors ({len(missing_timber)}):")
            for item in missing_timber:
                print(f"  - {item}")

        if missing_steel:
            print(f"Missing steel factors ({len(missing_steel)}):")
            for item in missing_steel:
                print(f"  - {item}")

        return results

    def _process_single_element(self, element: Dict) -> Dict:
        """Process a single element and return its results."""
        element_id = getattr(element, "id", "unknown")

        # Process element
        processed_element = self.element_processor.process_element(element)
        if not processed_element:
            return {
                "id": element_id,
                "status": "skipped",
                "reason": "Invalid element structure",
            }

        # Calculate carbon
        try:
            carbon_results = self.carbon_calculator.calculate_carbon(processed_element)
            return {
                "id": element_id,
                "status": "processed",
                "level": processed_element.level,
                "category": processed_element.category.value,
                "materials": [
                    {
                        "name": m.properties.name,
                        "type": m.type.value,
                        "volume": m.properties.volume,
                        # Add other material properties as needed
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

        # Ensure we're working with string values
        if hasattr(steel_db, "value"):
            steel_db = steel_db.value
        if hasattr(timber_db, "value"):
            timber_db = timber_db.value

        # Initialize analyzer
        analyzer = RevitCarbonAnalyzer(
            steel_database=steel_db,
            timber_database=timber_db,
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

        # Prepare detailed success message
        success_message = (
            f"🚀 Analysis complete.\n\n\tProcessed:\t\t{len(results['processed_elements'])} elements\n\t"
            f"Total carbon:\t{results['total_carbon']:.2f} kgCO₂e\n"
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
    # Group results by category
    successes: Dict[str, List[str]] = defaultdict(list)
    warnings: Dict[str, List[str]] = defaultdict(list)
    errors: Dict[str, List[str]] = defaultdict(list)

    # Group successful elements
    for element in results["processed_elements"]:
        successes["Carbon Analysis"].append(element["id"])

    # Group skipped elements
    for element in results["skipped_elements"]:
        warnings["Skipped Elements"].append(element["id"])

    # Group errors
    for element in results["errors"]:
        errors["Processing Errors"].append(element["id"])

    # Attach grouped results
    for category, object_ids in successes.items():
        automate_context.attach_success_to_objects(
            category=category,
            object_ids=object_ids,
            message="Carbon calculations completed successfully for these elements!",
        )

    for category, object_ids in warnings.items():
        automate_context.attach_warning_to_objects(
            category=category,
            object_ids=object_ids,
            message="Elements requiring careful review.",
        )

    for category, object_ids in errors.items():
        automate_context.attach_error_to_objects(
            category=category,
            object_ids=object_ids,
            message="Failure processing the following elements.",
        )


if __name__ == "__main__":
    execute_automate_function(automate_function, FunctionInputs)
