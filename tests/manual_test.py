# pytest: skip-file

from src.applications.revit.revit_material_processor import RevitMaterialProcessor
from src.applications.revit.revit_compliance import RevitCompliance
from src.applications.revit.revit_model import RevitModel
from src.applications.revit.revit_source_validator import RevitSourceValidator
from src.carbon.aggregator import MassAggregator
from src.applications.revit.revit_logger import RevitLogger

# Import required libraries
from specklepy.api.client import SpeckleClient
from specklepy.core.api import operations
from specklepy.transports.server import ServerTransport

# Define global variables
HOST = "https://app.speckle.systems/"
AUTHENTICATION_TOKEN = "840e5a18cda38ccc2a9ed8b52e9316530505c14181"
STREAM_ID = "99bdf924fb"
BRANCH_NAME = "2843"

# Setting up SpeckleClient and authenticating
client = SpeckleClient(host=HOST)
client.authenticate_with_token(token=AUTHENTICATION_TOKEN)

# Receiving commit
transport = ServerTransport(STREAM_ID, client)
branch = client.branch.get(stream_id=STREAM_ID, name=BRANCH_NAME)
model_data = operations.receive(branch.commits.items[0].referencedObject, transport)


def create_processor_chain() -> tuple[RevitModel, RevitLogger]:
    """
    Creates and configures the processing chain with all necessary dependencies.

    Returns:
        tuple[RevitModel, RevitLogger]:
            - Configured processor ready to handle Revit types
            - Logger instance for accessing compliance results
    """
    # Create core components
    logger = RevitLogger()
    mass_aggregator = MassAggregator()

    # Create processors
    material_processor = RevitMaterialProcessor(mass_aggregator, logger)
    compliance_checker = RevitCompliance(logger)

    # Create and return the main processor with logger
    return (
        RevitModel(
            material_processor=material_processor,
            compliance_checker=compliance_checker,
            logger=logger,
        ),
        logger,
    )


try:
    # Get version data
    commit_root = branch.commits.items[0]
    model_root = model_data

    # Validate source application
    source_validator = RevitSourceValidator()
    if not source_validator.validate_source_application(commit_root.sourceApplication):
        print(
            f"Automation requires Revit v3 commits. Received: {commit_root.sourceApplication}"
        )
    if not source_validator.validate_connector_version(
        int(getattr(model_root, "version", 2))
    ):
        print(
            "Automation required Revit models using the v3 " "connector. Received: v2."
        )

    # Create processor chain and get logger for results
    processor, logger = create_processor_chain()

    # Process model
    processor.process_elements(model_root)

    # Report compliance issues
    compliance_summary = logger.get_warnings_summary()

    print("Processing completed successfully.")

except Exception as e:
    print(f"Processing failed: {str(e)}")
    raise  # Re-raise for proper error tracking
