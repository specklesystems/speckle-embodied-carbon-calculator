from enum import Enum
from typing import Dict


class ConcreteElementType(Enum):
    GRADE_BEAM = "Grade Beam"
    SLAB_ON_GRADE = "Slab on Grade"
    PAD_FOOTING = "Pad Footing"
    PILE = "Pile"
    STRIP_FOOTING = "Strip Footing"
    PILE_CAP = "Pile Cap"
    GRAVITY_WALL = "Walls - wind/gravity"
    COLUMN = "Column"
    SHEAR_WALL = "Shear Walls"
    CONCRETE_SLAB = "Concrete Slabs"
    BEAM = "Beams"
    TOPPING_SLAB = "Topping Slabs"


class ReinforcementRates:
    """Reinforcement rates for concrete elements by element type."""

    def __init__(self, rates_dict: Dict[str, float]):
        """Initialize with rates provided from function inputs."""
        self._rates = {}

        # Convert string keys to enum values
        for type_str, rate in rates_dict.items():
            for enum_type in ConcreteElementType:
                if enum_type.value.lower() == type_str.lower():
                    self._rates[enum_type] = rate
                    break
            # If no match found, store with string key
            if type_str.lower() not in [e.value.lower() for e in ConcreteElementType]:
                self._rates[type_str] = rate

    def get_rate(self, element_type: str) -> float:
        """Get reinforcement rate for a concrete element type."""
        # Try direct match with enum values
        for enum_type in ConcreteElementType:
            if enum_type.value.lower() == element_type.lower():
                return self._rates.get(enum_type, 100.0)  # Default if missing

        # Try fuzzy matching with string keys
        element_lower = element_type.lower()
        if "beam" in element_lower and "grade" in element_lower:
            return self.get_rate_by_type(ConcreteElementType.GRADE_BEAM)
        elif "slab" in element_lower and "grade" in element_lower:
            return self.get_rate_by_type(ConcreteElementType.SLAB_ON_GRADE)
        # ... other fuzzy matching logic ...

        # Default value if no match found
        return 100.0

    def get_rate_by_type(self, element_type: ConcreteElementType) -> float:
        """Get rate by concrete element type enum."""
        return self._rates.get(element_type, 100.0)  # Default if missing
