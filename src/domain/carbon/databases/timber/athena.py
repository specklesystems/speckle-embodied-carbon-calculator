from src.domain.carbon.databases.enums import TimberDatabase
from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.schema import EmissionFactor

UNIT = "kgCO₂e/m³"


class Athena(EmissionFactorDatabase):
    def __init__(self):
        super().__init__()
        self._factors = {
            "Glulam": EmissionFactor(
                value=107,
                unit=UNIT,
                database=TimberDatabase.Athena2021.value,
                epd_number="ATHENA-2021-GL",
                publication_date="2021-01-01",
                valid_until="2026-01-01",
            ),
            "CLT": EmissionFactor(
                value=69,
                unit="kgCO2e/m3",
                database=TimberDatabase.Athena2021.value,
                epd_number=UNIT,
                publication_date="2021-01-01",
                valid_until="2026-01-01",
            ),
            "LVL": EmissionFactor(
                value=169,
                unit=UNIT,
                database=TimberDatabase.Athena2021.value,
                epd_number="ATHENA-2021-LVL",
                publication_date="2021-01-01",
                valid_until="2026-01-01",
            ),
            "Softwood Lumber": EmissionFactor(
                value=48,
                unit=UNIT,
                database=TimberDatabase.Athena2021.value,
                epd_number="ATHENA-2021-SWL",
                publication_date="2021-01-01",
                valid_until="2026-01-01",
            ),
            "Softwood Plywood": EmissionFactor(
                value=65,
                unit=UNIT,
                database=TimberDatabase.Athena2021.value,
                epd_number="ATHENA-2021-SWP",
                publication_date="2021-01-01",
                valid_until="2026-01-01",
            ),
            "Oriented Strand Board": EmissionFactor(
                value=182,
                unit=UNIT,
                database=TimberDatabase.Athena2021.value,
                epd_number="ATHENA-2021-OSB",
                publication_date="2021-01-01",
                valid_until="2026-01-01",
            ),
        }
