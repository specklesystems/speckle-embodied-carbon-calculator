from src.domain.carbon.databases.enums import TimberDatabase
from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.schema import EmissionFactor

UNIT = "kgCO₂e/m³"


class Structurlam(EmissionFactorDatabase):
    def __init__(self):
        super().__init__()
        self._factors = {
            "Glulam": EmissionFactor(
                value=115,
                unit=UNIT,
                database=TimberDatabase.Structurlam2020.value,
                epd_number="STR-2020-GL",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
            "CLT": EmissionFactor(
                value=124,
                unit=UNIT,
                database=TimberDatabase.Structurlam2020.value,
                epd_number="STR-2020-CLT",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
        }
