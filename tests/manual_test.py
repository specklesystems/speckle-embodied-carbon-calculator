# pytest: skip-file

from src.processors.material import RevitMaterialProcessor
from src.processors.compliance import RevitComplianceChecker
from src.processors.model import RevitModelProcessor
from src.validators.revit import RevitSourceValidator
from src.aggregators.carbon_totals import MassAggregator
from src.logging.compliance_logger import ComplianceLogger

# Import required libraries
from specklepy.api.client import SpeckleClient
from specklepy.core.api import operations
from specklepy.transports.server import ServerTransport

# Define global variables
HOST = "https://app.speckle.systems/"
AUTHENTICATION_TOKEN = "840e5a18cda38ccc2a9ed8b52e9316530505c14181"
STREAM_ID = "99bdf924fb"
BRANCH_NAME = "2391"

# Setting up SpeckleClient and authenticating
client = SpeckleClient(host=HOST)
client.authenticate_with_token(token=AUTHENTICATION_TOKEN)

# Receving commit
transport = ServerTransport(STREAM_ID, client)
branch = client.branch.get(stream_id=STREAM_ID, name=BRANCH_NAME)
model_data = operations.receive(branch.commits.items[0].referencedObject, transport)


def create_processor_chain() -> tuple[RevitModelProcessor, ComplianceLogger]:
    """
    Creates and configures the processing chain with all necessary dependencies.

    Returns:
        tuple[RevitModelProcessor, ComplianceLogger]:
            - Configured processor ready to handle Revit models
            - Logger instance for accessing compliance results
    """
    # Create core components
    logger = ComplianceLogger()
    mass_aggregator = MassAggregator()

    # Create processors
    material_processor = RevitMaterialProcessor(mass_aggregator)
    compliance_checker = RevitComplianceChecker(logger)

    # Create and return the main processor with logger
    return (
        RevitModelProcessor(
            material_processor=material_processor,
            compliance_checker=compliance_checker,
            logger=logger,
        ),
        logger,
    )


try:
    # Get version data
    commit_root = branch.commits.items[0]

    # Validate source application
    source_validator = RevitSourceValidator()
    if not source_validator.validate(commit_root.sourceApplication):
        print(
            f"Automation requires Revit v3 commits. Received: {commit_root.sourceApplication}"
        )

    # Create processor chain and get logger for results
    processor, logger = create_processor_chain()

    # Process model
    model_root = model_data
    processor.process_elements(model_root)

    # Report compliance issues
    compliance_summary = logger.get_warnings_summary()

    print("Processing completed successfully.")

except Exception as e:
    print(f"Processing failed: {str(e)}")
    raise  # Re-raise for proper error tracking
