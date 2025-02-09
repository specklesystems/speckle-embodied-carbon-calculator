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
        compliance_summary = logger.get_summary()
        for missing_property, elements in compliance_summary.items():
            automate_context.attach_warning_to_objects(
                category="Missing Revit Material Property",
                object_ids=elements,
                message=(
                    f"Missing {missing_property} on the object, preventing mass calculation. "
                    f"Update Revit object to contain the necessary properties if element is critical."
                ),
            )

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
