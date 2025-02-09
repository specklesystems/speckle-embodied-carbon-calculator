from pydantic import Field, SecretStr
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)

from src.processors.commit_processory import CommitProcessor


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
    # TODO: Add method to automation_context for sourceApplication
    version_id = automate_context.automation_run_data.triggers[0].payload.version_id
    commit_root = automate_context.speckle_client.commit.get(
        automate_context.automation_run_data.project_id, version_id
    )

    # ℹ️ sourceApplication value for v2: AppName + Version => Revit2024, Revit2023 etc.
    # ℹ️ sourceApplication value for v3: slug => revit
    # ⚠️ We're just working with v3 data - adapt commit_processor for v2 data structure if you want
    # ⚠️ Alternatively, write a model factory that injects the correct CommitProcessor()
    if commit_root.sourceApplication != "revit":
        automate_context.mark_run_failed(
            f"Automation built for v3 Revit commits. These are commits with a "
            f"case-sensitive sourceApplication == 'revit', not {commit_root.sourceApplication})"
        )

    # Process elements
    model_root = automate_context.receive_version()  # TODO: This is a waste!
    processor = CommitProcessor()
    processor.process_elements(model_root)

    compliance_summary = processor.logger.get_summary()
    for missing_property, elements in compliance_summary.items():
        automate_context.attach_warning_to_objects(
            category="Missing Revit Material Property",
            object_ids=elements,
            message=f"Missing {missing_property} on the object, preventing mass calculation. "
            f"Update Revit object to contain the necessary properties if element is critical. ",
        )

    # TODO: create_new_version_in_project
    automate_context.mark_run_success("Under development.")


if __name__ == "__main__":
    execute_automate_function(automate_function, FunctionInputs)
