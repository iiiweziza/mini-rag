from enum import Enum

class InputTypeEnum(str, Enum):
    FILE = "file"
    URL = "url"
    UNKNOWN = "unknown"