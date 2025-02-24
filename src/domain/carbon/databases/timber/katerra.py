from src.domain.carbon.databases.enums import TimberDatabase
from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.schema import EmissionFactor

UNIT = "kgCO₂e/m³"


class Katerra(EmissionFactorDatabase):
    def __init__(self):
        super().__init__()
        self._factors = {
            "CLT": EmissionFactor(
                value=158,
                unit=UNIT,
                database=TimberDatabase.Katerra2020.value,
                epd_number="KAT-2020-CLT",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
        }
