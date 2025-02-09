from abc import ABC, abstractmethod
from typing import Dict, List


class Logger(ABC):
    @abstractmethod
    def log_error(self, message: str, **kwargs) -> None:
        """Log an error message"""
        pass

    @abstractmethod
    def log_warning(self, message: str, **kwargs) -> None:
        """Log a warning message"""
        pass

    @abstractmethod
    def log_success(self, object_id: str, **kwargs) -> None:
        """Log a success message"""
        pass

    @abstractmethod
    def get_warnings_summary(self) -> Dict:
        """Get summary of logged warning messages"""
        pass

    @abstractmethod
    def get_successful_summary(self) -> List:
        """Get list of successfully processed elements"""
        pass
