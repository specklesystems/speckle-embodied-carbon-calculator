from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.databases.enums import TimberDatabase
from src.domain.carbon.schema import EmissionFactor

UNIT = "kgCO₂e/m³"


class CLFBaselineDocument(EmissionFactorDatabase):
    def __init__(self):
        super().__init__()
        self._factors = {
            "CLT": EmissionFactor(
                value=137,
                unit=UNIT,
                database=TimberDatabase.CLFBaselineDocument.value,
                epd_number="CLF-CLT",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
            "GLT/NLT/DLT": EmissionFactor(
                value=109,
                unit=UNIT,
                database=TimberDatabase.CLFBaselineDocument.value,
                epd_number="CLF-GLT",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
        }
