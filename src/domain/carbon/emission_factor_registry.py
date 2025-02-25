from typing import Optional, Dict

from src.domain.carbon.databases.concrete.metric import ConcreteEmissionDatabase
from src.domain.carbon.schema import EmissionFactor
from src.domain.carbon.databases.enums import (
    TimberDatabase,
    SteelDatabase,
    ConcreteDatabase,
)

# Import timber databases
from src.domain.carbon.databases.timber.athena import Athena
from src.domain.carbon.databases.timber.structurlam import Structurlam
from src.domain.carbon.databases.timber.awc_cwc import AwcCwc
from src.domain.carbon.databases.timber.katerra import Katerra
from src.domain.carbon.databases.timber.nordic_structures import NordicStructures
from src.domain.carbon.databases.timber.binderholz import Binderholz
from src.domain.carbon.databases.timber.structuralam_abbotsford import (
    StructuralamAbbotsford,
)
from src.domain.carbon.databases.timber.clf_baseline_document import CLFBaselineDocument
from src.domain.carbon.databases.timber.industry_average import IndustryAverage

# Import steel databases
from src.domain.carbon.databases.steel.steel_350_mpa import Steel350MPa


class EmissionFactorRegistry:
    """Registry of available emission factor databases"""

    def __init__(self):
        self._timber_databases = {}
        self._steel_databases = {}
        self._concrete_databases = {}

        # Material aliases for normalization
        # NOTE: Purely demonstrative → add aliases as needed.
        self._timber_aliases = {
            "clt": ["cross laminated timber", "cross-laminated timber"],
            "glulam": [
                "glue laminated timber",
                "glued laminated timber",
                "glulam beam",
            ],
            "lvl": ["laminated veneer lumber"],
            "softwood lumber": ["dimensional lumber", "sawn lumber", "softwood"],
            "softwood plywood": ["plywood", "softwood ply"],
            "oriented strand board": ["osb", "osb board"],
            "glt/nlt/dlt": [
                "glt",
                "nlt",
                "dlt",
                "nail laminated timber",
                "dowel laminated timber",
            ],
        }

        self._steel_aliases = {
            "hot rolled": [
                "hot-rolled",
                "hot_rolled",
                "hotrolled",
                "345 MPa",  # NOTE: Needed!
                "350W",  # NOTE: Needed!
                "350W(1)",  # NOTE: Needed!
            ],
            "hss": ["hollow structural section", "hollow section", "tube"],
            "plate": ["flat plate"],
            "rebar": ["reinforcing bar", "reinforcement"],
            "owsj": ["open web steel joist", "steel joist"],
            "fasteners": ["bolts", "screws", "nails", "rivets"],
            "metal deck": ["deck", "decking"],
        }

        self._concrete_aliases = {
            # To be added when concrete implementation is needed
        }

        # Initialize all database instances
        self._init_timber_databases()
        self._init_steel_databases()
        self._init_concrete_databases()

    def _init_timber_databases(self) -> None:
        """Initialize timber database implementations"""
        self._timber_databases = {
            TimberDatabase.Athena2021.value: Athena(),
            TimberDatabase.Structurlam2020.value: Structurlam(),
            TimberDatabase.AwcCwc2018.value: AwcCwc(),
            TimberDatabase.Katerra2020.value: Katerra(),
            TimberDatabase.NordicStructures2018.value: NordicStructures(),
            TimberDatabase.Binderholz2019.value: Binderholz(),
            TimberDatabase.StructuralamAbbotsford.value: StructuralamAbbotsford(),
            TimberDatabase.CLFBaselineDocument.value: CLFBaselineDocument(),
            TimberDatabase.IndustryAverage.value: IndustryAverage(),
        }

    def _init_steel_databases(self) -> None:
        """Initialize steel database implementations"""
        self._steel_databases = {
            SteelDatabase.Type350MPa.value: Steel350MPa(),
        }

    def _init_concrete_databases(self) -> None:
        """Initialize concrete database implementations"""
        self._concrete_databases = {
            ConcreteDatabase.GulLowAir.value: ConcreteEmissionDatabase(
                ConcreteDatabase.GulLowAir.value
            ),
            ConcreteDatabase.GulHighAir.value: ConcreteEmissionDatabase(
                ConcreteDatabase.GulHighAir.value
            ),
            ConcreteDatabase.GuLowAir.value: ConcreteEmissionDatabase(
                ConcreteDatabase.GuLowAir.value
            ),
            ConcreteDatabase.GuHighAir.value: ConcreteEmissionDatabase(
                ConcreteDatabase.GuHighAir.value
            ),
        }

    @staticmethod
    def _normalize_material_name(name: str, aliases: Dict[str, list]) -> str:
        """Normalize material name using centralized aliases with enhanced matching.

        This improved version handles:
        - Case insensitivity
        - Direct matches (exact)
        - Substring matches (contains)
        - Special known cases
        """

        # Convert to lowercase for case-insensitive comparison
        name = name.lower().strip()

        # Special case handling
        if any(
            steel_name in name
            for steel_name in ["345 mpa", "350w", "steel 345", "default_steel"]
        ):
            return "Hot Rolled"  # Map all these variants to Hot Rolled steel

        # Check for direct match with standard names
        for standard_name in aliases.keys():
            if standard_name.lower() == name:
                return standard_name

        # Check for standard name appearing as substring
        for standard_name in aliases.keys():
            if standard_name.lower() in name:
                return standard_name

        # Check aliases
        for standard_name, variations in aliases.items():
            for variation in variations:
                if variation.lower() == name or variation.lower() in name:
                    return standard_name

        return name

    def get_timber_factor(
        self, material_name: str, database: str
    ) -> Optional[EmissionFactor]:
        """Get emission factor for timber from specified database with name normalization"""
        db = self._timber_databases.get(database)
        if not db:
            raise ValueError(f"Unknown timber database: {database}")

        # Try direct lookup first
        factor = db.get_factor(material_name)
        if factor:
            return factor

        # If not found, try normalized name
        normalized_name = self._normalize_material_name(
            material_name, self._timber_aliases
        )
        return db.get_factor(normalized_name)

    def get_steel_factor(
        self, material_name: str, database: str
    ) -> Optional[EmissionFactor]:
        """Get emission factor for steel from specified database with name normalization"""
        db = self._steel_databases.get(database)
        if not db:
            raise ValueError(f"Unknown steel database: {database}")

        # Try direct lookup first
        factor = db.get_factor(material_name)
        if factor:
            return factor

        # If not found, try normalized name
        normalized_name = self._normalize_material_name(
            material_name, self._steel_aliases
        )
        return db.get_factor(normalized_name)

    def get_concrete_factor(
        self, strength: str, element_type: str, database: str
    ) -> Optional[EmissionFactor]:
        """Get emission factor for concrete from specified database based on strength and element type."""
        db = self._concrete_databases.get(database)
        if not db:
            raise ValueError(f"Unknown concrete database: {database}")

        # Concrete database requires both strength and element type
        return db.get_factor_by_strength_and_element(strength, element_type)

    def list_timber_databases(self) -> list[str]:
        """List all registered timber databases"""
        return list(self._timber_databases.keys())

    def list_steel_databases(self) -> list[str]:
        """List all registered steel databases"""
        return list(self._steel_databases.keys())

    def list_concrete_databases(self) -> list[str]:
        """List all registered concrete databases"""
        return list(self._concrete_databases.keys())
