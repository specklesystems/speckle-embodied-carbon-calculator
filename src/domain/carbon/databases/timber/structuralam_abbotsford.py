from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.databases.enums import TimberDatabase
from src.domain.carbon.schema import EmissionFactor

UNIT = "kgCO₂e/m³"


class StructuralamAbbotsford(EmissionFactorDatabase):
    def __init__(self):
        super().__init__()
        self._factors = {
            "Glulam": EmissionFactor(
                value=103,
                unit=UNIT,
                database=TimberDatabase.StructuralamAbbotsford.value,
                epd_number="SA-GL",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
        }
