import structlog
from typing import Dict, DefaultDict
from collections import defaultdict

logger = structlog.get_logger()


class ComplianceLogger:
    def __init__(self):
        self.missing_properties: DefaultDict[str, set] = defaultdict(set)

    def log_missing_properties(self, object_id: str, missing_property: str) -> None:
        # Log to our collection for automation results
        self.missing_properties[missing_property].add(object_id)

        # Still log individual cases for dev
        logger.warn(
            "non_compliant_element",
            object_id=object_id,
            property=missing_property,
            message=f"Missing: '{missing_property}' on object {object_id}. No computation on "
            f"for this object possible. Skipped.",
        )

    def get_summary(self) -> Dict[str, list]:
        return {
            prop: list(elements) for prop, elements in self.missing_properties.items()
        }
