from abc import ABC, abstractmethod
from typing import Dict, List


# TODO: Implementations use **kwargs which is silly. Formalize.
class Logger(ABC):
    """Interface for logging."""

    @abstractmethod
    def log_error(self, message: str, **kwargs) -> None:
        """Log an error.

        Args:
            message (str): error message
        """
        pass

    @abstractmethod
    def log_warning(self, message: str, **kwargs) -> None:
        """Log a warning.

        Args:
            message (str): warning message
        """
        pass

    @abstractmethod
    def log_success(self, object_id: str, **kwargs) -> None:
        """Log a success.

        Args:
            object_id (str): success message
        """
        pass

    @abstractmethod
    def get_warnings_summary(self) -> Dict:
        """Returns a dictionary of warning messages. The dictionary groups the warning types.

        Returns:
            Dict: {warning_type : [object_ids], ...}
        """
        pass

    @abstractmethod
    def get_successful_summary(self) -> List:
        """Returns a list of all successfully processed elements.

        Returns:
            List: [object_ids]
        """
        pass
