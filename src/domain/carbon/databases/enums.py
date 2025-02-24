from enum import Enum


class TimberDatabase(Enum):
    Athena2021 = "ATHENA 2021"
    Structurlam2020 = "Structurlam, 2020"
    AwcCwc2018 = "AWC, CWC, 2018"
    Katerra2020 = "Katerra, 2020"
    NordicStructures2018 = "Nordic Structures, 2018"
    Binderholz2019 = "Binderholz, 2019"
    StructuralamAbbotsford = "Structuralam Abbotsford"
    CLFBaselineDocument = "CLF Baseline Document"
    IndustryAverage = "INDUSTRY AVERAGE"


class SteelDatabase(Enum):
    Type350MPa = "Type 350 MPa"


class ConcreteDatabase(Enum):
    pass
