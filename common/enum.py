from enum import Enum


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


class InventoryType(Enum):
    tracker = 0x0
    equip = 0x1
    consume = 0x2
    install = 0x3
    etc = 0x4
    cash = 0x5