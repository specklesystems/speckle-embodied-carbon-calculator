from src.domain.carbon.databases.base import EmissionFactorDatabase
from src.domain.carbon.schema import EmissionFactor
from src.domain.carbon.databases.enums import ConcreteDatabase

UNIT = "kgCO₂e/m³"


class ConcreteEmissionDatabase(EmissionFactorDatabase):
    """Database implementation for concrete emission factors based on cement type and strength."""

    def __init__(self, database_name: str):
        super().__init__()
        self._database_name = database_name
        self._factors = {}
        self._init_factors()

    def _init_factors(self):
        """Initialize factors based on the specific database."""
        # Define mappings from database type to strength values
        database_strength_values = {
            ConcreteDatabase.GulLowAir.value: {
                "25": {
                    "Beam": 188,
                    "Slab": 188,
                    "Slab on Grade": 188,
                    "Foundation": 151,
                    "Column": 151,
                    "Wall": 151,
                    "Wall Foundation": 151,
                },
                "30": {
                    "Beam": 220,
                    "Slab": 220,
                    "Slab on Grade": 220,
                    "Foundation": 176,
                    "Column": 176,
                    "Wall": 176,
                    "Wall Foundation": 176,
                },
                "35": {
                    "Beam": 250,
                    "Slab": 250,
                    "Slab on Grade": 250,
                    "Foundation": 200,
                    "Column": 200,
                    "Wall": 200,
                    "Wall Foundation": 200,
                },
                "40": {
                    "Beam": 280,
                    "Slab": 280,
                    "Slab on Grade": 280,
                    "Foundation": 224,
                    "Column": 224,
                    "Wall": 224,
                    "Wall Foundation": 224,
                },
                "45": {
                    "Beam": 298,
                    "Slab": 298,
                    "Slab on Grade": 298,
                    "Foundation": 238,
                    "Column": 238,
                    "Wall": 238,
                    "Wall Foundation": 238,
                },
                "50": {
                    "Beam": 320,
                    "Slab": 320,
                    "Slab on Grade": 320,
                    "Foundation": 256,
                    "Column": 256,
                    "Wall": 256,
                    "Wall Foundation": 256,
                },
            },
            ConcreteDatabase.GulHighAir.value: {
                "25": {
                    "Beam": 201,
                    "Slab": 197,
                    "Slab on Grade": 197,
                    "Foundation": 157,
                    "Column": 157,
                    "Wall": 157,
                    "Wall Foundation": 157,
                },
                "30": {
                    "Beam": 236,
                    "Slab": 230,
                    "Slab on Grade": 230,
                    "Foundation": 184,
                    "Column": 184,
                    "Wall": 184,
                    "Wall Foundation": 184,
                },
                "35": {
                    "Beam": 268,
                    "Slab": 264,
                    "Slab on Grade": 264,
                    "Foundation": 211,
                    "Column": 211,
                    "Wall": 211,
                    "Wall Foundation": 211,
                },
                "40": {
                    "Beam": 292,
                    "Slab": 292,
                    "Slab on Grade": 292,
                    "Foundation": 234,
                    "Column": 234,
                    "Wall": 234,
                    "Wall Foundation": 234,
                },
                "45": {
                    "Beam": 316,
                    "Slab": 316,
                    "Slab on Grade": 316,
                    "Foundation": 254,
                    "Column": 254,
                    "Wall": 254,
                    "Wall Foundation": 254,
                },
                "50": {
                    "Beam": 343,
                    "Slab": 322,
                    "Slab on Grade": 322,
                    "Foundation": 257,
                    "Column": 257,
                    "Wall": 257,
                    "Wall Foundation": 257,
                },
            },
            ConcreteDatabase.GuLowAir.value: {
                "25": {
                    "Beam": 201,
                    "Slab": 201,
                    "Slab on Grade": 201,
                    "Foundation": 161,
                    "Column": 161,
                    "Wall": 161,
                    "Wall Foundation": 161,
                },
                "30": {
                    "Beam": 236,
                    "Slab": 236,
                    "Slab on Grade": 236,
                    "Foundation": 189,
                    "Column": 189,
                    "Wall": 189,
                    "Wall Foundation": 189,
                },
                "35": {
                    "Beam": 268,
                    "Slab": 268,
                    "Slab on Grade": 268,
                    "Foundation": 214,
                    "Column": 214,
                    "Wall": 214,
                    "Wall Foundation": 214,
                },
                "40": {
                    "Beam": 300,
                    "Slab": 300,
                    "Slab on Grade": 300,
                    "Foundation": 240,
                    "Column": 240,
                    "Wall": 240,
                    "Wall Foundation": 240,
                },
                "45": {
                    "Beam": 319,
                    "Slab": 319,
                    "Slab on Grade": 319,
                    "Foundation": 256,
                    "Column": 256,
                    "Wall": 256,
                    "Wall Foundation": 256,
                },
                "50": {
                    "Beam": 343,
                    "Slab": 343,
                    "Slab on Grade": 343,
                    "Foundation": 274,
                    "Column": 274,
                    "Wall": 274,
                    "Wall Foundation": 274,
                },
            },
            ConcreteDatabase.GuHighAir.value: {
                "25": {
                    "Beam": 210,
                    "Slab": 210,
                    "Slab on Grade": 210,
                    "Foundation": 168,
                    "Column": 168,
                    "Wall": 168,
                    "Wall Foundation": 168,
                },
                "30": {
                    "Beam": 246,
                    "Slab": 246,
                    "Slab on Grade": 246,
                    "Foundation": 197,
                    "Column": 197,
                    "Wall": 197,
                    "Wall Foundation": 197,
                },
                "35": {
                    "Beam": 283,
                    "Slab": 283,
                    "Slab on Grade": 283,
                    "Foundation": 227,
                    "Column": 227,
                    "Wall": 227,
                    "Wall Foundation": 227,
                },
                "40": {
                    "Beam": 313,
                    "Slab": 313,
                    "Slab on Grade": 313,
                    "Foundation": 251,
                    "Column": 251,
                    "Wall": 251,
                    "Wall Foundation": 251,
                },
                "45": {
                    "Beam": 339,
                    "Slab": 339,
                    "Slab on Grade": 339,
                    "Foundation": 271,
                    "Column": 271,
                    "Wall": 271,
                    "Wall Foundation": 271,
                },
                "50": {
                    "Beam": 345,
                    "Slab": 345,
                    "Slab on Grade": 345,
                    "Foundation": 276,
                    "Column": 276,
                    "Wall": 276,
                    "Wall Foundation": 276,
                },
            },
        }

        # Get the strength values for the selected database
        strength_values = database_strength_values.get(self._database_name)
        if not strength_values:
            raise ValueError(f"Unknown concrete database: {self._database_name}")

        # Create factors from the strength values
        for strength, elements in strength_values.items():
            for element, value in elements.items():
                factor_key = f"{strength}_{element}"
                self._factors[factor_key] = EmissionFactor(
                    value=value,
                    unit=UNIT,
                    database=self._database_name,
                    epd_number=f"CONCRETE-{self._database_name}-{strength}-{element}",
                    publication_date="2024-01-01",
                    valid_until="2029-01-01",
                )

    def get_factor_by_strength_and_element(
        self, strength: str, element_type: str
    ) -> EmissionFactor:
        """Get emission factor based on concrete strength and element type."""
        factor_key = f"{strength}_{element_type}"
        return self._factors.get(factor_key)
