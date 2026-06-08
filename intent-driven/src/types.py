from enum import Enum
from typing import Literal

class Area(str, Enum):
    REGISTRATION = 'registration'
    QUALIFICATION = 'qualification'
    COURSE = 'course'
    PATHWAY = 'pathway'
    UNI = 'university'
    FINALIZE = 'finalize'