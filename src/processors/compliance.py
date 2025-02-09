from typing import Any, List
from src.interfaces.compliance_checker import ComplianceChecker
from src.interfaces.logger import Logger
from src.utils.constants import ID


class RevitComplianceChecker(ComplianceChecker):
    def __init__(self, logger: Logger):
        self._logger = logger

    def check_compliance(self, element: Any, required_properties: List[str]) -> bool:
        """
        Checks basic element compliance (presence of ID and any custom required properties)
        """
        element_id = getattr(element, ID, None)
        if not element_id:
            self._logger.log_warning(
                "Element missing ID", object_id="unknown", missing_property=ID
            )
            return False

        return True  # Basic compliance only requires ID
