from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.databases.enums import TimberDatabase
from src.domain.carbon.schema import EmissionFactor

UNIT = "kgCO₂e/m³"


class NordicStructures(EmissionFactorDatabase):
    def __init__(self):
        super().__init__()
        self._factors = {
            "Glulam": EmissionFactor(
                value=100,
                unit=UNIT,
                database=TimberDatabase.NordicStructures2018.value,
                epd_number="NS-2018-GL",
                publication_date="2018-01-01",
                valid_until="2023-01-01",
            ),
            "CLT": EmissionFactor(
                value=122,
                unit=UNIT,
                database=TimberDatabase.NordicStructures2018.value,
                epd_number="NS-2018-CLT",
                publication_date="2018-01-01",
                valid_until="2023-01-01",
            ),
        }
