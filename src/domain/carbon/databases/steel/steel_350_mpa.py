from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.schema import EmissionFactor
from src.domain.carbon.databases.enums import SteelDatabase

UNIT = "kgCO₂e/kg"


class Steel350MPa(EmissionFactorDatabase):
    """Database implementation for Type 350 MPa steel emission factors."""

    def __init__(self):
        super().__init__()
        self._factors = {
            "Hot Rolled": EmissionFactor(
                value=1.22,
                unit=UNIT,
                database=SteelDatabase.Type350MPa.value,
                epd_number="STEEL-350-HR",
                publication_date="2024-01-01",
                valid_until="2029-01-01",
            ),
            "HSS": EmissionFactor(
                value=1.99,
                unit=UNIT,
                database=SteelDatabase.Type350MPa.value,
                epd_number="STEEL-350-HSS",
                publication_date="2024-01-01",
                valid_until="2029-01-01",
            ),
            "Plate": EmissionFactor(
                value=1.73,
                unit=UNIT,
                database=SteelDatabase.Type350MPa.value,
                epd_number="STEEL-350-PL",
                publication_date="2024-01-01",
                valid_until="2029-01-01",
            ),
            "Rebar": EmissionFactor(
                value=0.854,
                unit=UNIT,
                database=SteelDatabase.Type350MPa.value,
                epd_number="STEEL-350-RB",
                publication_date="2024-01-01",
                valid_until="2029-01-01",
            ),
            "OWSJ": EmissionFactor(
                value=1.380,
                unit=UNIT,
                database=SteelDatabase.Type350MPa.value,
                epd_number="STEEL-350-OWSJ",
                publication_date="2024-01-01",
                valid_until="2029-01-01",
            ),
            "Fasteners": EmissionFactor(
                value=1.730,
                unit=UNIT,
                database=SteelDatabase.Type350MPa.value,
                epd_number="STEEL-350-FST",
                publication_date="2024-01-01",
                valid_until="2029-01-01",
            ),
            "Metal Deck": EmissionFactor(
                value=2.370,
                unit=UNIT,
                database=SteelDatabase.Type350MPa.value,
                epd_number="STEEL-350-MD",
                publication_date="2024-01-01",
                valid_until="2029-01-01",
            ),
        }

        # Set up common aliases for steel types
        self._material_aliases = {
            "hot rolled": ["hot-rolled", "hot_rolled", "hotrolled"],
            "hss": ["hollow structural section", "hollow section", "tube steel"],
            "plate": ["steel plate", "flat plate"],
            "rebar": ["reinforcing bar", "reinforcement"],
            "owsj": ["open web steel joist", "steel joist"],
            "fasteners": ["bolts", "screws", "nails", "rivets"],
            "metal deck": ["steel deck", "decking"],
        }
