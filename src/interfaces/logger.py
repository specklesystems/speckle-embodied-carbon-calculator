from abc import ABC, abstractmethod
from typing import Dict


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
    def get_summary(self) -> Dict:
        """Get summary of logged messages"""
        pass
