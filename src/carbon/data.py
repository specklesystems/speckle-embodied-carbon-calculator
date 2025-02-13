
from enum import Enum
from types import WoodSupplier
from src.core.types import ( MetalClass, WoodClass )

"""kgCO2e/kg"""
metal_factors = {
    MetalClass.HOT_ROLLED: 1.22,
    MetalClass.HSS:	1.99,
    MetalClass.PLATE: 1.73,
    MetalClass.REBAR: 0.854,
    MetalClass.OWSJ: 1.380,
    MetalClass.FASTENERS: 1.730,
    MetalClass.METAL_DECK: 2.370,
}

"""kgCO2e/m3"""
wood_factors = {
    WoodSupplier.INDUSTRY_AVERAGE: {
        WoodClass.GLULAM: 113,
        WoodClass.CLT: 135,
        WoodClass.LVL: 265,
        WoodClass.SOFTWOOD_LUMBER: 56,
        WoodClass.SOFTWOOD_PLYWOOD: 142,
        WoodClass.WOOD_JOISTS: 2,
        WoodClass.REDWOOD_LUMBER: 38,
        WoodClass.ORIENTED_STRAND_BOARD: 212,
        WoodClass.GLT_NLT_DLT: 123
    },
    WoodSupplier.ATHENA: {
        WoodClass.GLULAM: 107,
        WoodClass.CLT: 69,
        WoodClass.LVL: 169,
        WoodClass.SOFTWOOD_LUMBER: 48,
        WoodClass.SOFTWOOD_PLYWOOD: 65,
        WoodClass.WOOD_JOISTS: None,
        WoodClass.REDWOOD_LUMBER: None,
        WoodClass.ORIENTED_STRAND_BOARD: 182,
        WoodClass.GLT_NLT_DLT: 0
    },
    WoodSupplier.STRUCTURLAM: {
        WoodClass.GLULAM: 115,
        WoodClass.CLT: 124,
        WoodClass.LVL: None,
        WoodClass.SOFTWOOD_LUMBER: None,
        WoodClass.SOFTWOOD_PLYWOOD: None,
        WoodClass.WOOD_JOISTS: None,
        WoodClass.REDWOOD_LUMBER: None,
        WoodClass.ORIENTED_STRAND_BOARD: None,
        WoodClass.GLT_NLT_DLT: 0
    },
     WoodSupplier.AWC_CWC: {
        WoodClass.GLULAM: 137,
        WoodClass.CLT: 0,
        WoodClass.LVL: 361,
        WoodClass.SOFTWOOD_LUMBER: 63,
        WoodClass.SOFTWOOD_PLYWOOD: 219,
        WoodClass.WOOD_JOISTS: 2,
        WoodClass.REDWOOD_LUMBER: 38,
        WoodClass.ORIENTED_STRAND_BOARD: 243,
        WoodClass.GLT_NLT_DLT: 0
    },
     WoodSupplier.KATERRA: {
        WoodClass.GLULAM: None,
        WoodClass.CLT: 158,
        WoodClass.LVL: None,
        WoodClass.SOFTWOOD_LUMBER: None,
        WoodClass.SOFTWOOD_PLYWOOD: None,
        WoodClass.WOOD_JOISTS: None,
        WoodClass.REDWOOD_LUMBER: None,
        WoodClass.ORIENTED_STRAND_BOARD: None,
        WoodClass.GLT_NLT_DLT: 0
    },
     WoodSupplier.NORDIC_STRUCTURES: {
        WoodClass.GLULAM: 100,
        WoodClass.CLT: 122,
        WoodClass.LVL: None,
        WoodClass.SOFTWOOD_LUMBER: None,
        WoodClass.SOFTWOOD_PLYWOOD: None,
        WoodClass.WOOD_JOISTS: None,
        WoodClass.REDWOOD_LUMBER: None,
        WoodClass.ORIENTED_STRAND_BOARD: None,
        WoodClass.GLT_NLT_DLT: 0
    },
     WoodSupplier.BINDERHOLZ: {
        WoodClass.GLULAM: 118,
        WoodClass.CLT: 200,
        WoodClass.LVL: None,
        WoodClass.SOFTWOOD_LUMBER: None,
        WoodClass.SOFTWOOD_PLYWOOD: None,
        WoodClass.WOOD_JOISTS: None,
        WoodClass.REDWOOD_LUMBER: None,
        WoodClass.ORIENTED_STRAND_BOARD: None,
        WoodClass.GLT_NLT_DLT: 0
    }
}


