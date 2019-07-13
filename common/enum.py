from enum import Enum

class ServerType(Enum):
    center =    0x00
    login =     0x01
    channel =   0x02
    shop =      0x03

class ServerRegistrationResponse(Enum):
    Valid =         0x00
    InvalidType =   0x01
    InvalidCode =   0x02
    Full =          0x03

class Worlds(Enum):
    Scania  =   0
    Broa    =   1
    Windia  =   2 
    Khaini  =   3
    Bellocan =  4
    Mardia  =   5
    Kradia  =   6
    Yellonde =  7
    Galacia =   8
    El_Nido =   9
    Zenith  =   11
    Arcenia =   12
    Judis   =   13
    Plana   =   14
    Kastia  =   15
    Kalluna =   16
    Stius   =   17
    Croa    =   18
    Medere  =   19

class WorldFlag(Enum):
    Null =  0x00
    Event = 0x01
    New =   0x02
    Hot =   0x03