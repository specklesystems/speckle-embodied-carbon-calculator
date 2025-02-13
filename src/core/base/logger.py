from typing import Dict, Optional
from abc import ABC, abstractmethod


class Logger(ABC):
    """Abstract base class for logging functionality"""

    @abstractmethod
    def log_error(
        self, object_id: str, category: str, message: Optional[str] = None
    ) -> None:
        """Log an error for a specific object"""
        pass

    @abstractmethod
    def log_warning(
        self, object_id: str, category: str, message: Optional[str] = None
    ) -> None:
        """Log a warning for a specific object"""
        pass

    @abstractmethod
    def log_success(
        self, object_id: str, category: str, message: Optional[str] = None
    ) -> None:
        """Log a success for a specific object"""
        pass

    @abstractmethod
    def log_info(
        self, object_id: str, category: str, message: Optional[str] = None
    ) -> None:
        """Log information for a specific object"""
        pass

    @abstractmethod
    def get_warnings_summary(self) -> Dict[str, list]:
        """Get summary of all warnings grouped by category"""
        pass

    @abstractmethod
    def get_errors_summary(self) -> Dict[str, list]:
        """Get summary of all errors grouped by category"""
        pass

    @abstractmethod
    def get_success_summary(self) -> Dict[str, list]:
        """Get summary of all successes grouped by category"""
        pass

    @abstractmethod
    def get_info_summary(self) -> Dict[str, list]:
        """Get summary of all info logs grouped by category"""
        pass
