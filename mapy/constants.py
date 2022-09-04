from enum import Enum, IntEnum


class Worlds(IntEnum):
    SCANIA = 0
    BROA = 1
    WINDIA = 2
    KHAINI = 3
    BELLOCAN = 4
    MARDIA = 5
    KRADIA = 6
    YELLONDE = 7
    GALACIA = 8
    EL_NIDO = 9
    ZENITH = 11
    ARCENIA = 12
    JUDIS = 13
    PLANA = 14
    KASTIA = 15
    KALLUNA = 16
    STIUS = 17
    CROA = 18
    MEDERE = 19


class Network:
    __registered_channels__ = {}

    HOST_IP = "127.0.0.1"
    SERVER_ADDRESS = bytearray([127, 0, 0, 1])

    # CENTER_PORT = center.sock
    LOGIN_PORT = 8484
    __GAME_PORT = 8585
    SHOP_PORT = 8787
    DATABASE_TYPE = "postgres"  # postgres / mariadb / mysql
    USE_DATABASE = False
    CHANNEL_COUNT = 3
    ACTIVE_WORLDS = [Worlds.BELLOCAN, Worlds.EL_NIDO, Worlds.GALACIA]
    # DB_HOST = ""
    # DB_PASS = ""
    # DB_PORT = 5432
    # DB_DATABASE = ""
    # DB_SCHEMA = ""

    # * Optionally:
    # DSN = "postgres://user:password@host:port/database"

    USE_HTTP_API = True
    HTTP_API_ROUTE = "/api"
    HTTP_HOST = "127.0.0.1", 8080
    STATISTICS = True

    @classmethod
    @property
    def GAME_PORT(cls):
        cls.__GAME_PORT += 1
        return cls.__GAME_PORT


class Config:
    # VERSION = 105
    # SUB_VERSION = "1"
    # LOCALE = 8

    VERSION = 95
    SUB_VERSION = "1"
    LOCALE = 8

    WORLD_COUNT = 1
    CHANNEL_COUNT = 4

    EXP_RATE = 1
    QUEST_EXP = 1
    PARTY_QUEST_EXP = 1
    MESO_RATE = 1
    DROP_RATE = 1

    LOG_PACKETS = True

    AUTO_LOGIN = False
    AUTO_REGISTER = True
    REQUEST_PIN = False
    REQUEST_PIC = False
    REQUIRE_STAFF_IP = False
    MAX_CHARACTERS = 3

    DEFAULT_EVENT_MESSAGE = "Wow amazing world choose this one"
    DEFAULT_TICKER = "Welcome"
    ALLOW_MULTI_LEVELING = False
    DEFAULT_CREATION_SLOTS = 3
    DISABLE_CHARACTER_CREATION = True


PERMANENT = 150841440000000000

ANTIREPEAT_BUFFS = [
    11101004,
    5221000,
    11001001,
    5211007,
    5121000,
    5121007,
    5111007,
    4341000,
    5111007,
    4121000,
    4201003,
    2121000,
    1221000,
    1201006,
    1211008,
    1211009,
    1211010,
    1121000,
    1001003,
    1101006,
    1111007,
    2101001,
    2101003,
    1321000,
    1311007,
    1311006,
]

EVENT_VEHICLE_SKILLS = [
    1025,
    1027,
    1028,
    1029,
    1030,
    1031,
    1033,
    1034,
    1035,
    1036,
    1037,
    1038,
    1039,
    1040,
    1042,
    1044,
    1049,
    1050,
    1051,
    1052,
    1053,
    1054,
    1063,
    1064,
    1065,
    1069,
    1070,
    1071,
]


def is_event_vehicle_skill(skill_id):
    return skill_id % 10000 in EVENT_VEHICLE_SKILLS


def get_job_from_creation(job_id):
    return {0: 3000, 1: 0, 2: 1000, 3: 2000, 4: 2001}.get(job_id, 0)


def is_extend_sp_job(job_id):
    return job_id / 1000 == 3 or job_id / 100 == 22 or job_id == 2001


class WorldFlag(IntEnum):
    Null = 0x00
    Event = 0x01
    New = 0x02
    Hot = 0x03


class InventoryType(IntEnum):
    TRACKER = 0x0
    EQUIP = 0x1
    CONSUME = 0x2
    INSTALL = 0x3
    ETC = 0x4
    CASH = 0x5


class ItemType(IntEnum):
    EQUIP = 10
    CONSUMABLE = 20
    RECHARGABLE = 21
    SETUP = 30
    ETC = 40
    CASH = 50
    PET = 51


class StatModifiers(IntEnum):
    def __new__(cls, value: int, encode_type: str):
        cls.encode = encode_type
        obj = int.__new__(cls, value)
        obj._value_ = value
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
