from functools import lru_cache
from typing import Optional, Dict, List, cast

from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.databases.concrete.metric import ConcreteEmissionDatabase
from src.domain.carbon.databases.enums import (
    TimberDatabase,
    SteelDatabase,
    ConcreteDatabase,
)
from src.domain.carbon.schema import EmissionFactor
from src.domain.carbon.material_alias_service import MaterialAliasService
from src.domain.carbon.databases.database_factory import DatabaseFactory


class EmissionFactorRegistry:
    """Registry of available emission factor databases with lazy loading."""

    def __init__(self):
        self._timber_databases: Dict[str, EmissionFactorDatabase] = {}
        self._steel_databases: Dict[str, EmissionFactorDatabase] = {}
        self._concrete_databases: Dict[str, ConcreteEmissionDatabase] = {}

        # Create the alias service
        self._alias_service = MaterialAliasService()

    def _get_timber_database(self, database_name: str) -> EmissionFactorDatabase:
        """Get or create a timber database instance."""
        if database_name not in self._timber_databases:
            self._timber_databases[
                database_name
            ] = DatabaseFactory.create_timber_database(database_name)
        return self._timber_databases[database_name]

    def _get_steel_database(self, database_name: str) -> EmissionFactorDatabase:
        """Get or create a steel database instance."""
        if database_name not in self._steel_databases:
            self._steel_databases[
                database_name
            ] = DatabaseFactory.create_steel_database(database_name)
        return self._steel_databases[database_name]

    def _get_concrete_database(self, database_name: str) -> ConcreteEmissionDatabase:
        """Get or create a concrete database instance."""
        if database_name not in self._concrete_databases:
            # We need to cast here because the factory returns the base type
            concrete_db = cast(
                ConcreteEmissionDatabase,
                DatabaseFactory.create_concrete_database(database_name),
            )
            self._concrete_databases[database_name] = concrete_db
        return self._concrete_databases[database_name]

    @lru_cache(maxsize=128)
    def get_timber_factor(
        self, material_name: str, database: str
    ) -> Optional[EmissionFactor]:
        """Get emission factor for timber from specified database with name normalization."""
        db = self._get_timber_database(database)

        # Try direct lookup first
        factor = db.get_factor(material_name)
        if factor:
            return factor

        # If not found, try normalized name
        normalized_name = self._alias_service.normalize_timber_name(material_name)
        return db.get_factor(normalized_name)

    @lru_cache(maxsize=128)
    def get_steel_factor(
        self, material_name: str, database: str
    ) -> Optional[EmissionFactor]:
        """Get emission factor for steel from specified database with name normalization."""
        db = self._get_steel_database(database)

        # Try direct lookup first
        factor = db.get_factor(material_name)
        if factor:
            return factor

        # If not found, try normalized name
        normalized_name = self._alias_service.normalize_steel_name(material_name)
        return db.get_factor(normalized_name)

    @lru_cache(maxsize=128)
    def get_concrete_factor(
        self, strength: str, element_type: str, database: str
    ) -> Optional[EmissionFactor]:
        """Get emission factor for concrete from specified database based on strength and element type."""
        db = self._get_concrete_database(database)

        # Now we can safely call this method since we've ensured the correct type
        return db.get_factor_by_strength_and_element(strength, element_type)

    @staticmethod
    def list_timber_databases() -> List[str]:
        """List all available timber databases."""
        return [db.value for db in TimberDatabase]

    @staticmethod
    def list_steel_databases() -> List[str]:
        """List all available steel databases."""
        return [db.value for db in SteelDatabase]

    @staticmethod
    def list_concrete_databases() -> List[str]:
        """List all available concrete databases."""
        return [db.value for db in ConcreteDatabase]
