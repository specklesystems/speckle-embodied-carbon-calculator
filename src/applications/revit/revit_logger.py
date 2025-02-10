import structlog
from typing import Dict, DefaultDict
from collections import defaultdict

from src.core.base.logger import Logger  # Import the interface

# NOTE: Only provide docstring if not covered by base class


class RevitLogger(Logger):
    """Implements Logger interface"""

    def __init__(self):
        self.missing_properties: DefaultDict[str, set] = defaultdict(set)
        self.successful_elements: set = set()
        self._structlog = structlog.get_logger()

    def log_error(self, message: str, **kwargs) -> None:
        self._structlog.error(message, **kwargs)

    def log_warning(self, message: str, **kwargs) -> None:
        """Log a warning message.
        Categorises and caches missing properties if 'missing_property' and 'object_id' specified in the kwargs.

        Args:
            message: Warning message to log
            **kwargs: Additional context. If 'object_id' and 'missing_property' are
                     provided, they will be tracked for compliance reporting.
        """
        self._structlog.warn(message, **kwargs)

        # Track missing properties if relevant kwargs are provided
        object_id = kwargs.get("object_id")
        missing_property = kwargs.get("missing_property")
        if object_id and missing_property:
            self.missing_properties[missing_property].add(object_id)

    def log_success(self, object_id: str, **kwargs) -> None:
        self._structlog.info(f"Successfully processed element", object_id=object_id)
        self.successful_elements.add(object_id)

    def get_warnings_summary(self) -> Dict[str, list]:
        return {
            prop: list(elements) for prop, elements in self.missing_properties.items()
        }

    def get_successful_summary(self) -> list:
        return list(self.successful_elements)
