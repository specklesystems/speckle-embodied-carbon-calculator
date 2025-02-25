from typing import Dict, Type

from src.domain.carbon.databases.base import EmissionFactorDatabase
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

# Import concrete databases
from src.domain.carbon.databases.concrete.metric import ConcreteEmissionDatabase


class DatabaseFactory:
    """Factory for creating emission factor database instances."""

    _timber_database_classes: Dict[str, Type[EmissionFactorDatabase]] = {
        TimberDatabase.Athena2021.value: Athena,
        TimberDatabase.Structurlam2020.value: Structurlam,
        TimberDatabase.AwcCwc2018.value: AwcCwc,
        TimberDatabase.Katerra2020.value: Katerra,
        TimberDatabase.NordicStructures2018.value: NordicStructures,
        TimberDatabase.Binderholz2019.value: Binderholz,
        TimberDatabase.StructuralamAbbotsford.value: StructuralamAbbotsford,
        TimberDatabase.CLFBaselineDocument.value: CLFBaselineDocument,
        TimberDatabase.IndustryAverage.value: IndustryAverage,
    }

    _steel_database_classes: Dict[str, Type[EmissionFactorDatabase]] = {
        SteelDatabase.Type350MPa.value: Steel350MPa,
    }

    @classmethod
    def create_timber_database(cls, database_name: str) -> EmissionFactorDatabase:
        """Create a timber database instance by name."""
        if database_name not in cls._timber_database_classes:
            raise ValueError(
                f"Unknown timber database: '{database_name}'. "
                f"Available databases: {', '.join(cls._timber_database_classes.keys())}"
            )
        return cls._timber_database_classes[database_name]()

    @classmethod
    def create_steel_database(cls, database_name: str) -> EmissionFactorDatabase:
        """Create a steel database instance by name."""
        if database_name not in cls._steel_database_classes:
            raise ValueError(
                f"Unknown steel database: '{database_name}'. "
                f"Available databases: {', '.join(cls._steel_database_classes.keys())}"
            )
        return cls._steel_database_classes[database_name]()

    @classmethod
    def create_concrete_database(cls, database_name: str) -> EmissionFactorDatabase:
        """Create a concrete database instance by name."""
        # For concrete, we create a new instance with the database name
        try:
            return ConcreteEmissionDatabase(database_name)
        except ValueError as e:
            # Re-raise with more context
            available_databases = [db.value for db in ConcreteDatabase]
            raise ValueError(
                f"Error creating concrete database: {str(e)}. "
                f"Available databases: {', '.join(available_databases)}"
            )
