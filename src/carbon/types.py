from enum import Enum
from dataclasses import dataclass

class WoodSupplier(str, Enum):
    INDUSTRY_AVERAGE = "Industry Average"
    ATHENA = "Athena, 2021"
    STRUCTURLAM = "Structurlam, 2020"
    AWC_CWC = "AWC, CWC, 2018"
    KATERRA = "Katerra, 2020"
    NORDIC_STRUCTURES = "Nordic Structures, 2018"
    BINDERHOLZ = "Binderholz, 2019"


@dataclass
class CarbonData:
    """Data class for embodied carbon data"""

    factor: float
    embodied_carbon: float
