from enum import Enum

class ServerType(Enum):
    center = 0x00
    login = 0x01
    channel = 0x02
    shop = 0x03

class ServerRegistrationResponse(Enum):
    Valid = 0x00
    InvalidType = 0x01
    InvalidCode = 0x02
    Full = 0x03

class WorldFlag(Enum):
    Null = 0x00
    Event = 0x01
    New = 0x02
    Hot = 0x03