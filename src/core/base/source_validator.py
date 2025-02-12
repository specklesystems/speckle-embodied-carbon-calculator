from abc import ABC, abstractmethod


class SourceApplicationValidator(ABC):
    """Interface for source application validator.
    Host app should be supported by the automation.
    """

    @abstractmethod
    def validate_source_application(self, source_app: str) -> bool:
        """Assert that the source application is supported."""
        pass

    @abstractmethod
    def validate_connector_version(self, connector_version: str) -> bool:
        """Assert that the connector version is supported."""
        pass
