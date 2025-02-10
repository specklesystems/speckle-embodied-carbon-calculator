from abc import ABC, abstractmethod


class SourceApplicationValidator(ABC):
    """Interface for source application validator.
    Host app should be supported by the automation.
    """
    @abstractmethod
    def validate(self, source_app: str) -> bool:
        """Assert that the source application is supported.

        Args:
            source_app (str): sourceApplication from the commit root

        Returns:
            bool: True if supported, False if not
        """
        pass
