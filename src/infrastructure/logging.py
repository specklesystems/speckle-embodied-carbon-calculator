import structlog
from typing import Dict, Set, Optional
from collections import defaultdict


class Logging:
    """Implements Logger interface with category-based logging"""

    def __init__(self):
        self._structlog = structlog.get_logger()
        self._errors: Dict[str, Set[str]] = defaultdict(set)
        self._warnings: Dict[str, Set[str]] = defaultdict(set)
        self._successes: Dict[str, Set[str]] = defaultdict(set)
        self._info: Dict[str, Set[str]] = defaultdict(set)

    def log_error(
        self, object_id: str, category: str, message: Optional[str] = None
    ) -> None:
        """Log an error for a specific object under a category"""
        self._errors[category].add(object_id)
        if message:
            self._structlog.error(message, object_id=object_id, category=category)
        else:
            self._structlog.error(
                "Error logged", object_id=object_id, category=category
            )

    def log_warning(
        self, object_id: str, category: str, message: Optional[str] = None
    ) -> None:
        """Log a warning for a specific object under a category"""
        self._warnings[category].add(object_id)
        if message:
            self._structlog.warning(message, object_id=object_id, category=category)
        else:
            self._structlog.warning(
                "Warning logged", object_id=object_id, category=category
            )

    def log_success(
        self, object_id: str, category: str, message: Optional[str] = None
    ) -> None:
        """Log a success for a specific object under a category"""
        self._successes[category].add(object_id)
        if message:
            self._structlog.info(message, object_id=object_id, category=category)
        else:
            self._structlog.info(
                "Success logged", object_id=object_id, category=category
            )

    def log_info(
        self, object_id: str, category: str, message: Optional[str] = None
    ) -> None:
        """Log information for a specific object under a category"""
        self._info[category].add(object_id)
        if message:
            self._structlog.info(message, object_id=object_id, category=category)
        else:
            self._structlog.info(
                "Information logged", object_id=object_id, category=category
            )

    @staticmethod
    def _convert_sets_to_lists(data: Dict[str, Set[str]]) -> Dict[str, list]:
        """Convert set values to lists in dictionary"""
        return {category: list(objects) for category, objects in data.items()}

    def get_warnings_summary(self) -> Dict[str, list]:
        """Get all warnings grouped by category"""
        return self._convert_sets_to_lists(self._warnings)

    def get_errors_summary(self) -> Dict[str, list]:
        """Get all errors grouped by category"""
        return self._convert_sets_to_lists(self._errors)

    def get_success_summary(self) -> Dict[str, list]:
        """Get all successes grouped by category"""
        return self._convert_sets_to_lists(self._successes)

    def get_info_summary(self) -> Dict[str, list]:
        """Get all info logs grouped by category"""
        return self._convert_sets_to_lists(self._info)
