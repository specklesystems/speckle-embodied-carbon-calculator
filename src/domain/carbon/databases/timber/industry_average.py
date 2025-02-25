from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.databases.enums import TimberDatabase
from src.domain.carbon.schema import EmissionFactor

UNIT = "kgCO₂e/m³"


class IndustryAverage(EmissionFactorDatabase):
    def __init__(self):
        super().__init__()
        self._factors = {
            "Glulam": EmissionFactor(
                value=113,
                unit=UNIT,
                database=TimberDatabase.IndustryAverage.value,
                epd_number="IA-GL",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
            "CLT": EmissionFactor(
                value=135,
                unit=UNIT,
                database=TimberDatabase.IndustryAverage.value,
                epd_number="IA-CLT",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
            "LVL": EmissionFactor(
                value=265,
                unit=UNIT,
                database=TimberDatabase.IndustryAverage.value,
                epd_number="IA-LVL",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
            "Softwood Lumber": EmissionFactor(
                value=56,
                unit=UNIT,
                database=TimberDatabase.IndustryAverage.value,
                epd_number="IA-SWL",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
            "Softwood Plywood": EmissionFactor(
                value=142,
                unit=UNIT,
                database=TimberDatabase.IndustryAverage.value,
                epd_number="IA-SWP",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
            "Wood Joists": EmissionFactor(
                value=2,
                unit=UNIT,
                database=TimberDatabase.IndustryAverage.value,
                epd_number="IA-WJ",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
            "Redwood Lumber": EmissionFactor(
                value=38,
                unit=UNIT,
                database=TimberDatabase.IndustryAverage.value,
                epd_number="IA-RWL",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
            "Oriented Strand Board": EmissionFactor(
                value=212,
                unit=UNIT,
                database=TimberDatabase.IndustryAverage.value,
                epd_number="IA-OSB",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
            "GLT/NLT/DLT": EmissionFactor(
                value=123,
                unit=UNIT,
                database=TimberDatabase.IndustryAverage.value,
                epd_number="IA-GLT",
                publication_date="2020-01-01",
                valid_until="2025-01-01",
            ),
        }
