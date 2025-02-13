from pydantic import Field, SecretStr
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)

from src.applications.revit.revit_material_processor import RevitMaterialProcessor
from src.applications.revit.revit_compliance import RevitCompliance
from src.applications.revit.revit_model import RevitModel
from src.applications.revit.revit_source_validator import RevitSourceValidator
from src.carbon.aggregator import MassAggregator
from src.applications.revit.revit_logger import RevitLogger
from src.core.base import Model


# TODO: Function inputs
class FunctionInputs(AutomateBase):
    """User-defined function inputs."""

    whisper_message: SecretStr = Field(title="This is a secret message")
    forbidden_speckle_type: str = Field(
        title="Forbidden speckle type",
        description=(
            "If a object has the following speckle_type,"
            " it will be marked with an error."
        ),
    )


def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:
    """Program entry point."""
    try:
        # Get version data
        version_id = automate_context.automation_run_data.triggers[0].payload.version_id
        commit_root = automate_context.speckle_client.commit.get(
            automate_context.automation_run_data.project_id, version_id
        )
        model_root = automate_context.receive_version()

        # Validate source application
        source_validator = RevitSourceValidator()  # Built for revit, therefore check
        if not source_validator.validate_source_application(
            commit_root.sourceApplication
        ):
            automate_context.mark_run_failed(
                f"Automation requires models from Revit. Received: {commit_root.sourceApplication}"
            )
            return
        if not source_validator.validate_connector_version(
            int(getattr(model_root, "version", 2))
        ):
            automate_context.mark_run_failed(
                "Automation required Revit models using the v3 "
                "connector. Received: v2."
            )
            return

        # Create processor chain and get logger for results
        processor = configure_components()

        # Process model
        processor.process_elements(model_root)

        # Logger information - successes
        (
            logger_successes,
            logger_infos,
            logger_warnings,
            logger_failures,
        ) = processor.get_processing_results()

        for category, object_ids in logger_successes.items():
            automate_context.attach_success_to_objects(
                category=category,
                object_ids=object_ids,
                message="Carbon calculations completed successfully for these elements.",
            )

        for category, object_ids in logger_infos.items():
            automate_context.attach_info_to_objects(
                category=category,
                object_ids=object_ids,
                message="Elements deemed not applicable and skipped.",
            )

        for category, object_ids in logger_warnings.items():
            automate_context.attach_warning_to_objects(
                category=category,
                object_ids=object_ids,
                message="Elements requiring careful review.",
            )

        for category, object_ids in logger_failures.items():
            automate_context.attach_error_to_objects(
                category=category,
                object_ids=object_ids,
                message="Failure processing the following elements.",
            )

        # TODO: Create new version
        # automate_context.create_new_version_in_project(model_root, "dev", "")

        automate_context.mark_run_success("Processing completed successfully.")

    except Exception as e:
        automate_context.mark_run_failed(f"Processing failed: {str(e)}")
        raise  # Re-raise for proper error tracking


# TODO instead of hard-coding revit, demo a factory method to inject implementations based on
#  function input
def configure_components() -> Model:
    """Configures and wires up processor components with dependencies.

    Creates core system components (logger, aggregator) and configures processors
    with required dependencies injected.

    Returns:
        tuple:
            - Model: Main processor configured with dependencies
    """

    # Core components
    logger = RevitLogger()  # For tracking issues
    mass_aggregator = MassAggregator()  # For collecting computed masses
    # TODO: results_aggregator = ResultAggregator and get rid of mass_aggregator

    # Create processors
    material_processor = RevitMaterialProcessor(
        mass_aggregator, logger
    )  # Material handler to "inject"
    compliance_checker = RevitCompliance(logger)  # Compliance checker to "inject"

    # Create and return the main processor with dependencies "injected"
    return RevitModel(
        material_processor=material_processor,
        compliance_checker=compliance_checker,
        logger=logger,
    )


if __name__ == "__main__":
    execute_automate_function(automate_function, FunctionInputs)
