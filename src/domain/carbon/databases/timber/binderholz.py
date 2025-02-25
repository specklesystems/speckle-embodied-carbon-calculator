from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.databases.enums import TimberDatabase
from src.domain.carbon.schema import EmissionFactor

UNIT = "kgCO₂e/m³"


class Binderholz(EmissionFactorDatabase):
    def __init__(self):
        super().__init__()
        self._factors = {
            "Glulam": EmissionFactor(
                value=118,
                unit=UNIT,
                database=TimberDatabase.Binderholz2019.value,
                epd_number="BH-2019-GL",
                publication_date="2019-01-01",
                valid_until="2024-01-01",
            ),
            "CLT": EmissionFactor(
                value=200,
                unit=UNIT,
                database=TimberDatabase.Binderholz2019.value,
                epd_number="BH-2019-CLT",
                publication_date="2019-01-01",
                valid_until="2024-01-01",
            ),
        }
