from enum import Enum

class MetalClass(Enum):
    HOT_ROLLED = "Hot Rolled"
    HSS = "HSS"
    PLATE = "Plate"
    REBAR = "Rebar"
    OWSJ = "OWSJ"
    FASTENERS = "Fasteners"
    METAL_DECK = "Metal Deck"

class WoodClass(Enum):
    GLULAM = "Glulam"
    CLT = "CLT"
    LVL = "LVL"
    SOFTWOOD_LUMBER = "Softwood Lumber"
    SOFTWOOD_PLYWOOD = "Softwood Plywood"
    WOOD_JOISTS = "Wood Joists"
    REDWOOD_LUMBER = "Redwood Lumber"
    ORIENTED_STRAND_BOARD = "Oriented Strand Board"
    GLT_NLT_DLT = "GLT/NLT/DLT"