from pydantic import Field, SecretStr
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)

from src.processors.material import RevitMaterialProcessor
from src.processors.compliance import RevitComplianceChecker
from src.processors.model import RevitModelProcessor
from src.validators.revit import RevitSourceValidator
from src.aggregators.carbon_totals import MassAggregator
from src.logging.compliance_logger import ComplianceLogger


class FunctionInputs(AutomateBase):
    # An example of how to use secret values.
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

        # Validate source application
        source_validator = RevitSourceValidator()  # Built for revit, therefore check
        if not source_validator.validate(commit_root.sourceApplication):
            automate_context.mark_run_failed(
                f"Automation requires Revit v3 commits. Received: {commit_root.sourceApplication}"
            )
            return

        # Create processor chain and get logger for results
        processor, logger = create_processor_chain()

        # Process model
        model_root = automate_context.receive_version()  # TODO: Line 35 and 36!?
        processor.process_elements(model_root)

        # Report compliance issues
        logger_warnings = logger.get_warnings_summary()
        if logger_warnings:
            for missing_property, elements in logger_warnings.items():
                automate_context.attach_warning_to_objects(
                    category="Missing Required Revit Properties",
                    object_ids=elements,
                    message=(
                        f"Property '{missing_property}' is missing, which prevents carbon "
                        f"calculations. If this element is critical to your analysis, please "
                        f"update its Revit properties."
                    ),
                )

        logger_successes = logger.get_successful_summary()
        if logger_successes:
            automate_context.attach_success_to_objects(
                category="Successfully Processed",
                object_ids=logger_successes,
                message="Carbon calculations completed successfully for this element.",
            )

        # TODO: Create new version
        # automate_context.create_new_version_in_project(model_root, "dev", "")

        automate_context.mark_run_success("Processing completed successfully.")

    except Exception as e:
        automate_context.mark_run_failed(f"Processing failed: {str(e)}")
        raise  # Re-raise for proper error tracking


def create_processor_chain() -> tuple[RevitModelProcessor, ComplianceLogger]:
    """Creates and configures the required components."""

    # Core components
    logger = ComplianceLogger()  # For tracking issues
    mass_aggregator = MassAggregator()  # For collecting computed masses

    # Create processors
    material_processor = RevitMaterialProcessor(mass_aggregator)  # Material calcs
    compliance_checker = RevitComplianceChecker(logger)  # Validation

    # Create and return the main processor with logger
    return (
        RevitModelProcessor(
            material_processor=material_processor,
            compliance_checker=compliance_checker,
            logger=logger,
        ),
        logger,
    )


if __name__ == "__main__":
    execute_automate_function(automate_function, FunctionInputs)
