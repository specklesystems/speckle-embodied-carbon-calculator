from src.domain.carbon.databases.enums import TimberDatabase
from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.schema import EmissionFactor

UNIT = "kgCO₂e/m³"


class AwcCwc(EmissionFactorDatabase):
    def __init__(self):
        super().__init__()
        self._factors = {
            "Glulam": EmissionFactor(
                value=137,
                unit=UNIT,
                database=TimberDatabase.AwcCwc2018.value,
                epd_number="AWC-2018-GL",
                publication_date="2018-01-01",
                valid_until="2023-01-01",
            ),
            "LVL": EmissionFactor(
                value=361,
                unit=UNIT,
                database=TimberDatabase.AwcCwc2018.value,
                epd_number="AWC-2018-LVL",
                publication_date="2018-01-01",
                valid_until="2023-01-01",
            ),
            "Softwood Lumber": EmissionFactor(
                value=63,
                unit=UNIT,
                database=TimberDatabase.AwcCwc2018.value,
                epd_number="AWC-2018-SWL",
                publication_date="2018-01-01",
                valid_until="2023-01-01",
            ),
            "Softwood Plywood": EmissionFactor(
                value=219,
                unit=UNIT,
                database=TimberDatabase.AwcCwc2018.value,
                epd_number="AWC-2018-SWP",
                publication_date="2018-01-01",
                valid_until="2023-01-01",
            ),
            "Wood Joists": EmissionFactor(
                value=2,
                unit=UNIT,
                database=TimberDatabase.AwcCwc2018.value,
                epd_number="AWC-2018-WJ",
                publication_date="2018-01-01",
                valid_until="2023-01-01",
            ),
            "Redwood Lumber": EmissionFactor(
                value=38,
                unit=UNIT,
                database=TimberDatabase.AwcCwc2018.value,
                epd_number="AWC-2018-RWL",
                publication_date="2018-01-01",
                valid_until="2023-01-01",
            ),
            "Oriented Strand Board": EmissionFactor(
                value=243,
                unit=UNIT,
                database=TimberDatabase.AwcCwc2018.value,
                epd_number="AWC-2018-OSB",
                publication_date="2018-01-01",
                valid_until="2023-01-01",
            ),
        }
