import pytest

from src.domain.carbon.databases.enums import TimberDatabase, SteelDatabase
from src.domain.carbon.emission_factor_registry import EmissionFactorRegistry


class TestRegistry:
    """Test suite for the EmissionFactorRegistry"""

    @pytest.fixture
    def registry(self):
        """Create and return a registry instance"""
        return EmissionFactorRegistry()

    def test_timber_database_lookup(self, registry):
        """Test direct lookup of timber factors"""
        # Test each database
        factor = registry.get_timber_factor(
            "FE_CLT Floor Panel (1)", TimberDatabase.Athena2021.value
        )
        assert factor is not None
        assert factor.value == 69

        factor = registry.get_timber_factor(
            "FE_Glulam", TimberDatabase.Binderholz2019.value
        )
        assert factor is not None
        assert factor.value == 118

    def test_steel_database_lookup(self, registry):
        """Test direct lookup of steel factors"""
        factor = registry.get_steel_factor(
            "Metal - Steel CSA G40", SteelDatabase.Type350MPa.value
        )
        assert factor is not None
        assert factor.value == 1.22

    def test_invalid_database(self, registry):
        """Test error handling for invalid database"""
        with pytest.raises(ValueError, match="Unknown timber database"):
            registry.get_timber_factor("CLT", "NonExistentDatabase")
