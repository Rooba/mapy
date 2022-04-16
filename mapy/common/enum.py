from enum import Enum


class Worlds(Enum):
    Scania = 0
    Broa = 1
    Windia = 2
    Khaini = 3
    Bellocan = 4
    Mardia = 5
    Kradia = 6
    Yellonde = 7
    Galacia = 8
    El_Nido = 9
    Zenith = 11
    Arcenia = 12
    Judis = 13
    Plana = 14
    Kastia = 15
    Kalluna = 16
    Stius = 17
    Croa = 18
    Medere = 19


class WorldFlag(Enum):
    Null = 0x00
    Event = 0x01
    New = 0x02
    Hot = 0x03


class InventoryType(Enum):
    TRACKER = 0x0
    EQUIP = 0x1
    CONSUME = 0x2
    INSTALL = 0x3
    ETC = 0x4
    CASH = 0x5


class StatModifiers(int, Enum):
    encode: str

    def __new__(cls, value, encode_type):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.encode = encode_type
        return obj

    SKIN = (0x1, "byte")
    FACE = (0x2, "int")
    HAIR = (0x4, "int")

    PET = (0x8, "long")
    PET2 = (0x80000, "long")
    PET3 = (0x100000, "long")

    LEVEL = (0x10, "byte")
    JOB = (0x20, "short")
    STR = (0x40, "short")
    DEX = (0x80, "short")
    INT = (0x100, "short")
    LUK = (0x200, "short")

    HP = (0x400, "int")
    MAX_HP = (0x800, "int")
    MP = (0x1000, "int")
    MAX_MP = (0x2000, "int")

    AP = (0x4000, "short")
    SP = (0x8000, "short")

    EXP = (0x10000, "int")
    POP = (0x20000, "short")

    MONEY = (0x40000, "int")
    # TEMP_EXP = 0x200000
