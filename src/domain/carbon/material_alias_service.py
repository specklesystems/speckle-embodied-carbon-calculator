from typing import Dict, List, Optional


class MaterialAliasService:
    """Service for managing and resolving material name aliases"""

    def __init__(self):
        # Material aliases used for normalization
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
                "345 MPa",
                "350W",
                "350W(1)",
                "Steel ASTM A500B-42",
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

    def normalize_timber_name(self, name: str) -> str:
        return self._normalize_material_name(name, self._timber_aliases)

    def normalize_steel_name(self, name: str) -> str:
        return self._normalize_material_name(name, self._steel_aliases)

    def normalize_concrete_name(self, name: str) -> str:
        return self._normalize_material_name(name, self._concrete_aliases)

    @staticmethod
    def _normalize_material_name(name: str, aliases: Dict[str, List[str]]) -> str:
        """Normalize material name using centralized aliases with enhanced matching."""

        # Convert to lowercase for case-insensitive comparison
        name = name.lower().strip()

        # Special case handling
        if any(
            steel_name in name
            for steel_name in [
                "345 mpa",
                "350w",
                "steel 345",
                "default_steel",
                "Steel ASTM A500B-42",
            ]
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
