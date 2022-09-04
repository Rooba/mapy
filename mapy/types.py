import asyncio
from abc import ABCMeta, abstractmethod
from asyncio import AbstractEventLoop, Event, Lock, Queue, Task, get_event_loop
from datetime import datetime
from enum import Enum, EnumMeta, IntEnum
from inspect import ismethod
from io import BytesIO
from ipaddress import IPv4Address
from random import SystemRandom
from socket import socket
from types import new_class
from typing import (
    IO,
    Any,
    Callable,
    Coroutine,
    Generator,
    Literal,
    NewType,
    Type,
    TypeVar,
)
from uuid import UUID, uuid4

from attrs import define, field
from typing_extensions import Self

from .constants import WorldFlag, Worlds, is_extend_sp_job
from .game.inventory import InventoryManager
from .logger import Logger

rng = SystemRandom("570279009")

sock: socket = field(default=socket())

TaskType = NewType("TaskType", Task)

T = TypeVar("T")
Schema = Any
Column = Any
Table = Any
_Items = Type["GWItem"]
_Skills = Type["Skill"]
_World = Type["World"]
_Packet = Type["Packet"]

MapleCharacter = TypeVar("MapleCharacter", bound="MapleCharacter")


class Foo(Enum):
    ...


class T_c(EnumMeta):
    ...


_C = object()
F = new_class("F", (type(_C),), exec_body=lambda ns: {"__dict__": Any, "__all__": ns})


class OpCode(F.__dict__["__dict__"].__objclass__, Enum):
    Any: Any
    ...


class CRecvOps(OpCode, Enum):
    ...


class CSendOps(OpCode, Enum):
    ...


class Mapping(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def __getitem__(self, key):
        if not hasattr(self, key) or key.startswith("__"):
            return None
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
        self.__dict__[key] = value

    def __getattribute__(self, __name: str) -> Any:
        return object.__getattribute__(self, __name)

    def __iter(self):
        return tuple(
            (k, v)
            for k, v in self.__dict__.items()
            if not k.startswith("__") and not ismethod(v) and not callable(v)
        )

    def __iter__(self):
        return iter({k: v for k, v in self.__iter()})

    def keys(self):
        return iter({k: v for k, v in self.__iter()}.keys())

    def values(self):
        return iter({k: v for k, v in self.__iter()}.values())

    def items(self):
        return iter({k: v for k, v in self.__iter()}.items())

    def __get__(self, key):
        return getattr(self, key, None)

    def __set__(self, key, value):
        setattr(self, key, value)
        self.__dict__[key] = value

    def __repr__(self):
        return str({k: v for k, v in self.items()})


class StatModifiers(int, Enum):
    SKIN = 0x1, 1
    FACE = 0x2, 4
    HAIR = 0x4, 4

    PET = 0x8, 8
    PET2 = 0x80000, 8
    PET3 = 0x100000, 8

    LEVEL = 0x10, 1
    JOB = 0x20, 2
    STR = 0x40, 2
    DEX = 0x80, 2
    INT = 0x100, 2
    LUK = 0x200, 2

    HP = 0x400, 4
    MAX_HP = 0x800, 4
    MP = 0x1000, 4
    MAX_MP = 0x2000, 4

    AP = 0x4000, 2
    SP = 0x8000, 2

    EXP = 0x10000, 4
    POP = 0x20000, 2

    MONEY = 0x40000, 4

    # FIXME: Not encoding anything atm

    def __new__(cls, value: int, bit_size: int):
        cls.__bit_size__ = bit_size
        cls._value_ = value
        return super().__new__(cls, value)

    def encode(self, packet: "Packet", value: int):
        # enc = {1: "byte", 2: "short", 4: "int", 8: "long"}.get(self.__bit_size__)
        # getattr(packet, f"encode_{enc}")()
        ...


@define
class Stats(Mapping):
    id: int = 0
    name: str = ""
    world_id: int = 0

    gender: int = 0
    skin: int = 0
    face: int = 20001
    hair: int = 30003
    level: int = 1
    job: int = 0

    _str: int = 4
    dex: int = 4
    _int: int = 4
    luk: int = 4
    hp: int = 50
    m_hp: int = 50
    mp: int = 5
    m_mp: int = 5

    ap: int = 0
    sp: int = 0
    extend_sp: list[int] = field(factory=lambda: list(bytearray(10)))

    exp: int = 0
    money: int = 0
    fame: int = 0
    temp_exp: int = 0

    field_id: int = 100000000
    portal: int = 0
    play_time: int = 0
    sub_job: int = 0
    pet_locker: list[int] = field(factory=lambda: list(bytearray(3)))

    def encode(self, packet) -> None:
        packet.encode_int(self.id)
        packet.encode_fixed_string(self.name, 13)
        packet.encode_byte(self.gender)
        packet.encode_byte(self.skin)
        packet.encode_int(self.face)
        packet.encode_int(self.hair)

        for sn in self.pet_locker:
            packet.encode_long(sn)

        packet.encode_byte(self.level)
        packet.encode_short(self.job)
        packet.encode_short(self._str)
        packet.encode_short(self.dex)
        packet.encode_short(self._int)
        packet.encode_short(self.luk)
        packet.encode_int(self.hp)
        packet.encode_int(self.m_hp)
        packet.encode_int(self.mp)
        packet.encode_int(self.m_mp)
        packet.encode_short(self.ap)

        # if player not evan
        packet.encode_short(self.sp)
        # else
        # packet.encode_byte(len(self.extend_sp))

        # for i, sp in enumerate(self.extend_sp):
        #     packet.encode_byte(i)
        #     packet.encode_byte(sp)

        packet.encode_int(self.exp)
        packet.encode_short(self.fame)
        packet.encode_int(self.temp_exp)
        packet.encode_int(self.field_id)
        packet.encode_byte(self.portal)
        packet.encode_int(self.play_time)
        packet.encode_short(self.sub_job)


class NpcScript(metaclass=ABCMeta):
    def __init__(self, npc_id, client, default=False):
        self._npc_id: int
        self._context: Any
        self._last_msg_type: Any
        self._prev_msgs: list[str]
        self._prev_id: int
        self._response: Queue

    @property
    def npc_id(self) -> int:
        ...

    @property
    def last_msg_type(self) -> Any:
        ...

    async def send_message(self, type_, action, flag=4, param=0) -> int:
        ...

    async def send_dialogue(self, type_, action, flag, param) -> None:
        ...

    async def reuse_dialogue(self, msg) -> None:
        ...

    async def proceed_back(self) -> None:
        ...

    async def proceed_next(self, resp) -> None:
        ...

    def end_chat(self) -> None:
        ...

    @staticmethod
    def get_script(npc_id, client) -> "NpcScript":
        ...


class Skill:
    def __init__(self, id: int):
        ...


class SkillLevel:
    def __init__(self, **kwargs):
        ...


@define
class SkillLevelData(object):
    flags: list[int] = field(factory=list)
    weapon: int = 0
    sub_weapon: int = 0
    max_level: int = 0
    base_max_level: int = 0
    skill_type: list = field(factory=list)
    element: str = field(factory=str)
    mob_count: str = field(factory=str)
    hit_count: str = field(factory=str)
    buff_time: str = field(factory=str)
    mp_cost: str = field(factory=str)
    hp_cost: str = field(factory=str)
    damage: str = field(factory=str)
    fixed_damage: str = field(factory=str)
    critical_damage: str = field(factory=str)
    _levels: dict = field(factory=dict)
    mastery: str = field(factory=str)

    def __post_init__(self):
        self._levels = {}
        for i in range(self.max_level):
            kwargs = {}
            for name, value in self.__dict__.items():
                if isinstance(value, str):
                    # kwargs[name] = rtl_equation(value, i)
                    pass
                else:
                    kwargs[name] = value

            self._levels[i] = SkillLevel(**kwargs)

    def __getitem__(self, index):
        return self._levels[index]


@define(kw_only=True)
class SkillEntry(object):
    id: int = 0
    level: int = 1
    mastery_level: int = 1
    max_level: int = 1
    expiration: int = 0
    level_data: list = field(factory=lambda: list(bytearray(10)))

    def encode(self, packet: "Packet") -> None:
        packet.encode_int(self.id)
        packet.encode_int(self.level)
        packet.encode_long(0)  # skill.expiration


class StatModifier(Mapping):
    def __init__(self, character_stats: Stats):
        self._modifiers: list[StatModifiers] = []
        for k, v in character_stats.items():
            self[k] = v

    @property
    def modifiers(self) -> list["StatModifiers"]:
        return self._modifiers

    @property
    def flag(self):
        _flag = 0
        for mod in self._modifiers:
            _flag |= mod.value
        return _flag

    def alter(self, **stats: dict[str, int | list[int]]):
        for key, val in stats.items():
            modifier = StatModifiers[key.upper()]
            self._modifiers.append(modifier)
            self[key] = val

    def encode(self, packet):
        packet.encode_int(self.flag)

        for modifier in StatModifiers:
            if modifier not in self._modifiers:
                continue

            if modifier is StatModifiers.SP:
                if is_extend_sp_job(self._stats.job):
                    packet.encode_byte(0)
                else:
                    packet.encode_short(self._stats.sp)
            else:
                getattr(packet, f"encode_{modifier.encode}")(
                    packet, getattr(self._stats, modifier.name.lower())
                )


@define
class PlayerModifiers(object):
    character: MapleCharacter

    def __init__(self, character: MapleCharacter):
        self.character = character

    async def stats(self, *, excl_req=True, **stats):
        from .cpacket import CPacket

        modifier = StatModifier(self.character.stats)
        modifier.alter(**stats)

        if modifier.modifiers:
            await self.character.send_packet(CPacket.stat_changed(modifier, excl_req))


class Loggable(metaclass=ABCMeta):
    _logger: Logger

    def __init__(self) -> None:
        self._logger: Logger = Logger(self)

    def log(self, message: str, level: int | str = 0):
        self._logger.log(message, level)


class MapleIV(metaclass=ABCMeta):
    _shuffle: bytearray = bytearray()

    def __init__(self, __vector: int) -> None:
        self.value: int

    def __int__(self) -> int:
        ...

    @property
    def hiword(self) -> int:
        ...

    @property
    def loword(self) -> int:
        ...

    def shuffle(self) -> None:
        ...


class ByteBuffer(IO, metaclass=ABCMeta):
    def encode(self, _bytes: bytes | bytearray):
        ...

    def encode_byte(self, value: int) -> Self:
        ...

    def encode_short(self, value: int) -> Self:
        ...

    def encode_int(self, value: int) -> Self:
        ...

    def encode_long(self, value: int) -> Self:
        ...

    def encode_buffer(self, buffer: bytearray | bytes) -> Self:
        ...

    def skip(self, count: int) -> Self:
        ...

    def encode_string(self, string: str) -> Self:
        ...

    def encode_fixed_string(self, string: str, length=13) -> Self:
        ...

    def encode_hex_string(self, string: str) -> Self:
        ...

    def decode_byte(self) -> int:
        ...

    def decode_bool(self) -> bool:
        ...

    def decode_short(self) -> int:
        ...

    def decode_int(self) -> int:
        ...

    def decode_long(self) -> int:
        ...

    def decode_buffer(self, size: int) -> str:
        ...

    def decode_string(self) -> str:
        ...


class Packet(ByteBuffer):
    def __init__(
        self, data: bytes | None = None, op_code: OpCode | None = None, raw=False
    ):
        self.op_code: OpCode

    @property
    def name(self) -> str:
        ...

    def to_array(self) -> list[bytes]:
        ...

    def to_string(self) -> str:
        ...

    def __len__(self) -> int:
        ...


class PacketHandler:
    def __init__(self, name: str, callback: Callable, **kwargs):
        self.name = name
        self.callback = callback
        self.op_code = kwargs.get("op_code")


def packet_handler(op_code=None) -> Any:
    def wrap(func: Callable[..., Coroutine]) -> "PacketHandler":
        return PacketHandler(func.__name__, func, op_code=op_code)

    return wrap


class QueryTable(metaclass=ABCMeta):
    ...


class AccountTable(QueryTable):
    ...


class GWItemTable(QueryTable):
    ...


class GWEquipTable(QueryTable):
    ...


class GWBundleTables(QueryTable):
    ...


class GWPetTable(QueryTable):
    ...


class InventoriesTables(QueryTable):  # i dont like this it gotta go
    ...


class FuncKeys(QueryTable):
    ...


class SkillsTable(QueryTable):
    ...


class Field(QueryTable):
    ...


class DatabaseClient(Loggable, Mapping, metaclass=ABCMeta):
    _name = "Database Client"

    def __init__(
        self, /, user: str, password: str, host: str, port: int, database: str
    ):
        Loggable.__init__(self)
        self._user = user
        self._pass = password
        self._host = host
        self._port = port
        self._database = database
        self._pool = None
        self._dsn = f"postgres://{user}:{password}@{host}:{port}/{database}"

        # WZ Data
        self._items: GWItemTable
        self._skills: SkillsTable

    @property
    def dsn(self):
        return self._dsn

    async def start(self):
        ...

    async def stop(self):
        ...

    async def recreate_pool(self):
        ...

    async def initialize_database(self):
        ...

    async def execute_query(self, query, *args):
        ...

    async def execute_transaction(self, query, *query_args):
        ...

    async def create_table(
        self, name: str, columns: list[Column | str], *, primaries=None
    ) -> Table:
        ...

    def table(self, name, *, schema: str | Schema | None = None) -> Table:
        ...

    def query(self, *tables):
        ...

    def insert(self, table):
        ...

    def update(self, table):
        ...

    def schema(self, name):
        ...

    # def account(self, *multi_acc, **single_acc):
    def account(self, **kwargs):
        ...

    def _accounts(self, *lookups):
        ...

    @property
    def characters(self):
        ...

    @property
    def field(self):
        ...

    @property
    def items(self) -> GWItemTable:
        return self._items

    @property
    def skills(self) -> SkillsTable:
        return self._skills


class WvsCenter(Loggable, metaclass=ABCMeta):
    """Server central coordinator for game / login servers

    Attributes
    ----------
    name : str
        Server specific name
    login : LoginServer
        Login server listener instance
    _worlds : dict[int, World]
        :obj:`dict` of :obj:`int` channel_id ->  :obj:`World` server instances
    shop: :class:`ShopServer`
        Connected `ShopServer`

    """

    RUNNING: Event = Event()

    def __init__(self):
        self._name: str
        self._loop: AbstractEventLoop
        self._clients: str
        self._pending_logins: list
        self._login: WvsLogin
        self._config: dict
        self._start_time: int
        self._shop: WvsShop
        self._worlds: dict[int, World]
        self._logger: Logger

    @property
    def data(self) -> "DatabaseClient":
        ...

    @property
    def login(self) -> "WvsLogin | None":
        ...

    @property
    def logger(self) -> Logger:
        ...

    @property
    def shop(self) -> "WvsShop | None":
        ...

    @shop.setter
    def shop(self, shop) -> None:
        ...

    @property
    def worlds(self) -> dict[int, "World"]:
        ...

    def log(self, message) -> None:
        ...

    def _load_config(self) -> None:
        ...

    def _make_config(self) -> None:
        ...

    def save_config(self, conf: dict | None = None) -> None:
        ...

    def _run(self) -> None:
        ...

    async def _start(self) -> None:
        ...

    @property
    def uptime(self) -> int:
        ...

    @property
    def population(self) -> int:
        ...


class ClientBase(Loggable, metaclass=ABCMeta):
    def __init__(self, *args, **kwargs) -> None:
        self._socket: socket
        self._port: int
        self._overflow_buff: memoryview | bytearray
        self._recv_buff: BytesIO
        self._logged_in: bool
        self._world_id: int
        self._channel_id: int
        self._lock: Lock
        self._m_riv: MapleIV
        self._m_siv: MapleIV
        self._logger: Logger

    @property
    def connected_channel(self):
        ...

    @property
    def ip(self) -> IPv4Address:
        ...

    @property
    def data(self) -> DatabaseClient:
        ...

    @property
    def identifier(self) -> tuple[str, int]:
        ...

    def dispatch(self, packet) -> None:
        ...

    def close(self) -> None:
        ...

    async def initialize(self) -> None:
        ...

    async def send_packet(self, out_packet) -> None:
        ...

    async def send_packet_raw(self, packet) -> None:
        ...

    def manipulate_buffer(self, buffer) -> None:
        ...


class WvsLoginClient(ClientBase):
    def __init__(self, socket: socket):
        self._account: Account
        self._avatars: list[Any]

    async def login(self, username: str, password: str) -> int:
        ...

    async def load_avatars(self, world_id=None) -> None:
        ...

    @property
    def account_id(self) -> int:
        return getattr(self._account, "id", -1)


class WvsGameClient(ClientBase):
    def __init__(self, socket):
        super().__init__(socket)
        self._channel_id: int
        self._world_id
        self._character: MapleCharacter
        self._npc_script: NpcScript
        self._sent_char_data: bool

    @property
    def world_id(self) -> int:
        if not self._logged_in:
            return -1

        return self._world_id

    async def broadcast(self, packet) -> None:
        ...

    def get_field(self) -> Field:
        ...


class ServerBase(Loggable, metaclass=ABCMeta):
    """Server base for center, channel, and login servers"""

    def __init__(self) -> None:

        self._name: str
        self._loop: AbstractEventLoop
        self._logger: Logger
        self._clients: list
        self._packet_handlers: list
        self._ready: Event
        self._alive: Event
        self._acceptor: asyncio.tasks._FutureLike
        self._serv_sock: socket

    @property
    def center(self) -> WvsCenter | None:
        ...

    @property
    def port(self) -> int:
        ...

    @port.setter
    def port(self, value: int) -> None:
        ...

    def log(self, message: str, level: str | None = None) -> None:
        ...

    @abstractmethod
    async def client_connect(self, client_sock: socket) -> ClientBase:
        ...

    @property
    def alive(self) -> bool:
        ...

    def start(self) -> None:
        ...

    def close(self) -> None:
        ...

    async def on_client_accepted(self, socket: socket):
        ...

    async def on_client_disconnect(self, client):
        ...

    def add_packet_handlers(self):
        ...

    def wait_until_ready(self) -> Coroutine[Any, Any, Literal[True]]:
        ...

    async def listen(self):
        ...

    @property
    def data(self) -> DatabaseClient:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def population(self) -> int:
        ...

    def push(self, client: ClientBase, packet: Packet) -> None:
        ...


class WvsGame(ServerBase):
    def __new__(cls, **data) -> "WvsGame":
        ...

    def __init__(self, **data):
        self.channel_id: int
        self._field_manager: dict
        ...

    async def client_connect(self, client: ClientBase) -> None:
        ...

    async def on_client_disconnect(self, client: ClientBase) -> None:
        ...

    async def get_field(self, field_id: Field):
        ...

    @packet_handler(CRecvOps)
    async def handle_migrate_in(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def handle_user_move(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def handle_skill_use_request(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def handle_user_select_npc(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def handle_user_script_message_answer(
        self, client: ClientBase, packet: Packet
    ):
        ...

    @packet_handler(CRecvOps)
    async def handle_update_gm_board(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def handle_require_field_obstacle(self, client: ClientBase, packet: Packet):
        ...


class WvsLogin(ServerBase):
    def __init__(self):
        self.port: int
        self._worlds: list[World]
        self._auto_register: bool
        self._request_pin: bool
        self._request_pic: bool
        self._require_staff_ip: bool
        self._max_characters: int
        self._login_pool: list[PendingLogin]

    def add_world(self, world: "World"):
        ...

    async def client_connect(self, client: ClientBase) -> None:
        ...

    @packet_handler(CRecvOps)
    async def create_secuirty_heandle(self, client: ClientBase, packet) -> None:
        ...

    @packet_handler(CRecvOps)
    async def check_password(self, client: ClientBase, packet: Packet) -> None:
        ...

    async def send_world_information(self, client: ClientBase) -> None:
        ...

    @packet_handler(CRecvOps)
    async def world_request(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def world_info_request(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def check_user_limit(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def select_world(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def logout_world(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def check_duplicated_id(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def view_all_characters(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def create_new_character(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps)
    async def select_character(self, client: ClientBase, packet: Packet):
        ...


class WvsShop(ServerBase):
    def __init__(self):
        pass


class World(metaclass=ABCMeta):
    def __init__(self: "World", id: int):
        self._world: Worlds
        self._channels: list[World]
        self._flag: WorldFlag
        self._allow_multi_leveling: bool
        self._default_creation_slots: int
        self._disable_character_creation: bool
        self._event_message: str
        self._ticker_message: str
        self._exp_rate: float
        self._quest_exp_rate: float
        self._party_quest_exp_rate: float
        self._meso_rate: float
        self._drop_rate: float
        self._id: int

    @property
    def id(self) -> int:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def port(self) -> int:
        ...

    @property
    def population(self) -> int:
        ...

    @property
    def channels(self) -> list[WvsGame]:
        ...

    def add_channel(self, item) -> None:
        ...

    def __getitem__(self, key) -> WvsGame:
        ...


class InventoryType(IntEnum):
    EQUIPPED = -1
    UNDEFINED = 0
    EQUIP = 1
    USE = 2
    SETUP = 3
    ETC = 4
    CASH = 5
    STORAGE = 6
    DUEY = 10
    MTS = 15
    FREDERICK = 20
    HIRED_MERCHANT = 21
    CASHSHOP = 25
    CASHSHOP_DUALBLADE = 26
    CASHSHOP_CANNONEER = 27
    CASHSHOP_CYGNUS = 30
    CASHSHOP_ARAN = 33
    CASHSHOP_EVAN = 34
    CASHSHOP_MERCEDES = 35
    CASHSHOP_RESISTENCE = 38
    CASHSHOP_DEMON = 39


@define
class GWItem(metaclass=ABCMeta):
    """Base item class for all items

    Parameters
    ----------
    item_id: int
        Item temaplte ID
    cisn: int
        Cash Inventory Serial Numer
        Used for tracking cash items
    expire: :class:`datetime.datetime`
        Expiry date of the item, if any
    inventory_item_id: int
        Primary key to store the item in database
    flag: bool
        Determines whether item has been deleted,
        transfered, or stayed in inventory

    """

    item_id: int = 0
    item_uuid: UUID = uuid4()
    cash_serial: int = 0
    source_type: int = 0
    expire: int = 0
    quantity: int = 0
    flag: int = 0

    def encode(self, packet: Packet) -> None:
        """Encode base item information onto packet

        Parameters
        ----------
        packet: :class:`net.packets.Packet`
            The packet to encode the data onto

        """

        packet.encode_int(self.item_id)
        packet.encode_byte(self.cash_serial == 0)

        if self.cash_serial:
            packet.encode_long(self.cash_serial)

        packet.encode_long(0)


@define
class GWEquip(GWItem):
    req_job: list[int] | None = list()
    ruc: int = 0
    cuc: int = 0

    _str: int = 0
    dex: int = 0
    _int: int = 0
    luk: int = 0
    hp: int = 0
    mp: int = 0
    weapon_attack: int = 0
    weapon_defense: int = 0
    magic_attack: int = 0
    magic_defense: int = 0
    accuracy: int = 0
    avoid: int = 0

    hands: int = 0
    speed: int = 0
    jump: int = 0

    title: str = ""
    craft: int = 0
    attribute: int = 0
    level_up_type: int = 0
    level: int = 0
    durability: int = 0
    iuc: int = 0
    exp: int = 0

    grade: int = 0
    chuc: int = 0

    option_1: int = 0
    option_2: int = 0
    option_3: int = 0
    socket_1: int = 0
    socket_2: int = 0

    lisn: int = 0
    storage_id: int = 0
    sn: int = 0

    def encode(self, packet: Packet) -> None:
        packet.encode_byte(1)

        super().encode(packet)

        packet.encode_byte(self.ruc)
        packet.encode_byte(self.cuc)
        packet.encode_short(self._str)
        packet.encode_short(self.dex)
        packet.encode_short(self._int)
        packet.encode_short(self.luk)
        packet.encode_short(self.hp)
        packet.encode_short(self.mp)
        packet.encode_short(self.weapon_attack)
        packet.encode_short(self.magic_attack)
        packet.encode_short(self.weapon_defense)
        packet.encode_short(self.magic_defense)
        packet.encode_short(self.accuracy)
        packet.encode_short(self.avoid)
        packet.encode_short(self.craft)
        packet.encode_short(self.speed)
        packet.encode_short(self.jump)
        packet.encode_string(self.title)
        packet.encode_short(self.attribute)

        packet.encode_byte(self.level_up_type)
        packet.encode_byte(self.level)
        packet.encode_int(self.exp)
        packet.encode_int(-1 & 0xFFFFFF)

        packet.encode_int(self.iuc)

        packet.encode_byte(self.grade)
        packet.encode_byte(self.chuc)

        packet.encode_short(self.option_1)
        packet.encode_short(self.option_2)
        packet.encode_short(self.option_3)
        packet.encode_short(self.socket_1)
        packet.encode_short(self.socket_2)

        if not self.cash_serial:
            packet.encode_long(0)

        packet.encode_long(0)
        packet.encode_int(0)


@define
class GWBundle(GWItem):
    attribute: int = 0
    lisn: int = 0
    title: str = ""

    def encode(self, packet: Packet) -> None:
        packet.encode_byte(2)

        super().encode(packet)

        packet.encode_short(self.quantity)
        packet.encode_string(self.title)
        packet.encode_short(self.attribute)

        if self.item_id / 10000 == 207:  # android/pet ie has_serial
            packet.encode_long(self.lisn)


class Inventory(metaclass=ABCMeta):
    inv_type: InventoryType
    items: dict[int, GWItem | None]
    _slots: int

    def __init__(self, inv_type: InventoryType, slots: int):
        ...
        self.inv_type: InventoryType
        self.items: dict[int, GWItem | None]
        self._slots: int

    def __getitem__(self, slot_idx: int) -> GWItem:
        ...

    def __iter__(self) -> Generator[GWItem, None, None] | None:
        if self.items:
            return (item for _, item in self.items.items() if item)

    def get_free_slot(self) -> int:
        for i in range(1, self._slots + 1):
            if not self.items[i]:
                return i

        return 0

    def add(self, item: GWItem, slot: int | None = None) -> tuple[int, GWItem | None]:
        items = None

        if isinstance(item, GWEquip):
            free_slot = self.get_free_slot() if not slot else slot

            if free_slot:
                self.items[free_slot] = item
                items = (free_slot, item)

        elif isinstance(item, GWBundle):
            pass

        if not items:
            return (0, None)

        return items

    @property
    def slots(self) -> int:
        return self._slots

    def encode(self, packet) -> None:
        for slot, item in self.items.items():
            if not item:
                continue

            packet.encode_byte(slot)
            item.encode(packet)

        packet.encode_byte(0)


@define
class MapleCharacter(metaclass=ABCMeta):
    random = rng

    def __init__(self, stats: dict | None = None) -> None:
        self._client: ClientBase | None

        self._field: None | Field
        self.stats: Stats
        self.inventories: InventoryManager
        self.func_keys: FuncKeys
        self.modify: PlayerModifiers
        self.skills: dict

        self.map_transfer: list[int]
        self.map_transfer_ex: list[int]
        self.monster_book_cover_id: int

    @property
    def id(self) -> int:
        ...

    @property
    def field_id(self) -> int:
        ...

    @property
    def client(self) -> ClientBase:
        ...

    @client.setter
    def client(self, value: ClientBase) -> None:
        ...

    @property
    def data(self) -> DatabaseClient:
        ...

    @data.setter
    def data(self, value: DatabaseClient) -> None:
        ...

    @property
    def equip_inventory(self) -> Inventory:
        ...

    @property
    def consume_inventory(self) -> Inventory:
        ...

    @property
    def install_inventory(self) -> Inventory:
        ...

    @property
    def etc_inventory(self) -> Inventory:
        ...

    @property
    def cash_inventory(self) -> Inventory:
        ...

    def encode_entry(self, packet: Packet):
        ...

    def encode(self, packet: Packet):
        ...

    def encode_inventories(self, packet):
        ...

    def encode_skills(self, packet):
        ...

    def encode_quests(self, packet):
        ...

    def encode_minigames(self, packet):
        ...

    def encode_rings(self, packet):
        ...

    def encode_teleports(self, packet):
        ...

    def encode_monster_book(self, packet):
        ...

    def encode_new_year(self, packet):
        ...

    def encode_area(self, packet):
        ...

    def encode_look(self, packet):
        ...

    async def send_packet(self, packet):
        if not self._client:
            raise ConnectionError

        await self._client.send_packet(packet)


@define
class Account:
    id: int
    username: str
    password: str
    gender: int
    creation: datetime
    last_login: datetime | None
    last_ip: IPv4Address
    ban: int
    admin: int
    last_connected_world: Worlds | None


@define
class PendingLogin:
    def __init__(self, character: MapleCharacter, account: Account, requested: Any):
        self.character: MapleCharacter
        self.char_id: int
        self.account: Account
        self.requested: Any
        self.migrated: bool
