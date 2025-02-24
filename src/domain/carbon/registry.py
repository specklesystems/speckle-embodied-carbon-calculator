from typing import Optional
from src.domain.carbon.schema import EmissionDatabase, EmissionFactor
from src.domain.carbon.databases.base import EmissionFactorDatabase


class EmissionFactorRegistry:
    """Registry of available emission factor databases"""

    def __init__(self):
        self._databases: dict[EmissionDatabase, EmissionFactorDatabase] = {}

    def register_database(
        self, database_type: EmissionDatabase, implementation: EmissionFactorDatabase
    ) -> None:
        """Register a new database implementation"""
        self._databases[database_type] = implementation

    def get_factor(
        self, material_name: str, database: EmissionDatabase
    ) -> Optional[EmissionFactor]:
        """Get emission factor from specified database"""
        db = self._databases.get(database)
        if not db:
            raise ValueError(f"Unknown database: {database}")
        return db.get_factor(material_name)

    def list_databases(self) -> list[EmissionDatabase]:
        """List all registered databases"""
        return list(self._databases.keys())
