from abc import ABCMeta, abstractmethod
from asyncio import AbstractEventLoop, Event, Lock
from datetime import datetime
from enum import EnumMeta, IntEnum
from io import BytesIO
from ipaddress import IPv4Address
from random import SystemRandom
from socket import socket
from types import (
    MethodDescriptorType,
    MethodType,
    MethodWrapperType,
    WrapperDescriptorType,
)
from typing import IO, Any, Callable, Coroutine, Generator, Literal, NewType, TypeVar
from uuid import UUID, uuid4

from attrs import define, field
from typing_extensions import Self

from .constants import WorldFlag, Worlds
from .game.character import PlayerModifiers, Stats
from .game.inventory import InventoryManager
from .logger import Logger

rng = SystemRandom("570279009")

sock: socket = field(default=socket())

T = TypeVar("T")
Schema = Any
Column = Any
Table = Any
_Items = NewType("_Items")
Items = _Items
_Skills = NewType("_Skills")
Skills = _Skills
_World = NewType("_World")
World = _World
_Packet = NewType("_Packet")
Packet = _Packet


class Loggable(ABCMeta):
    _logger: Logger

    def __init__(self) -> None:
        self._logger: Logger = Logger(self)

    def log(self, message: str, level: int | str = 0):
        self._logger.log(message, level)


class OpCode(Any, IntEnum, EnumMeta):
    ...


class CRecvOps(OpCode):
    ...


class CSendOps(OpCode):
    ...


class MapleIV(ABCMeta):
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


class ByteBuffer(IO, ABCMeta):
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


class QueryTable(ABCMeta):
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


class DatabaseClient(Loggable, ABCMeta):
    _name = "Database Client"

    def __init__(
        self, /, user: str, password: str, host: str, port: int, database: str
    ):
        super(Loggable, self).__init__(Loggable)
        self._user = user
        self._pass = password
        self._host = host
        self._port = port
        self._database = database
        self._pool = None
        self._dsn = f"postgres://{user}:{password}@{host}:{port}/{database}"

        # WZ Data
        self._items: Items
        self._skills: Skills

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
    def items(self) -> Items:
        return self._items

    @property
    def skills(self) -> Skills:
        return self._skills


class WvsCenter(Loggable, ABCMeta):
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


class ClientBase(Loggable, ABCMeta):
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
        super().__init__(socket)
        self._account: Account
        self._avatars: list[Any] = []

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
        self._npc_script: NPCScript
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


class ServerBase(Loggable, ABCMeta):
    """Server base for center, channel, and login servers"""

    def __init__(self) -> None:

        self._name: str
        self._loop: AbstractEventLoop
        self._logger: Logger
        self._clients: list
        self._packet_handlers: list
        self._ready: Event
        self._alive: Event
        self._acceptor: Acceptor
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

    @packet_handler(CRecvOps.CP_MigrateIn)
    async def handle_migrate_in(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_UserMove)
    async def handle_user_move(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_UserSkillUseRequest)
    async def handle_skill_use_request(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_UserSelectNpc)
    async def handle_user_select_npc(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_UserScriptMessageAnswer)
    async def handle_user_script_message_answer(
        self, client: ClientBase, packet: Packet
    ):
        ...

    @packet_handler(CRecvOps.CP_UpdateGMBoard)
    async def handle_update_gm_board(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_RequireFieldObstacleStatus)
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

    @packet_handler(CRecvOps.CP_CreateSecurityHandle)
    async def create_secuirty_heandle(self, client: ClientBase, packet) -> None:
        ...

    @packet_handler(CRecvOps.CP_CheckPassword)
    async def check_password(self, client: ClientBase, packet: Packet) -> None:
        ...

    async def send_world_information(self, client: ClientBase) -> None:
        ...

    @packet_handler(CRecvOps.CP_WorldRequest)
    async def world_request(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_WorldInfoRequest)
    async def world_info_request(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_CheckUserLimit)
    async def check_user_limit(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_SelectWorld)
    async def select_world(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_LogoutWorld)
    async def logout_world(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_CheckDuplicatedID)
    async def check_duplicated_id(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_ViewAllChar)
    async def view_all_characters(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_CreateNewCharacter)
    async def create_new_character(self, client: ClientBase, packet: Packet):
        ...

    @packet_handler(CRecvOps.CP_SelectCharacter)
    async def select_character(self, client: ClientBase, packet: Packet):
        ...


class WvsShop(ServerBase):
    def __init__(self):
        pass


class World(ABCMeta):
    def __init__(self: World, id: int):
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
class GWItem(ABCMeta):
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


class Inventory(ABCMeta):
    inv_type: InventoryType
    items: dict[int, GWItem | None]
    _slots: int

    def __init__(self, inv_type: InventoryType, slots: int):
        self.inv_type: InventoryType = inv_type
        self.items: dict[int, GWItem | None] = {i: None for i in range(slots)}
        self._slots: int = slots

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
class MapleCharacter(ABCMeta):
    def __init__(self, stats: dict | None = None) -> None:
        self._client: ClientBase | None = None

        if not stats:
            stats = {}

        self._field: None | Field = None
        self.stats: Stats = Stats(**stats)
        self.inventories: InventoryManager = InventoryManager(self)
        self.func_keys: FuncKeys = FuncKeys(self)
        self.modify: PlayerModifiers = PlayerModifiers(self)
        self.skills: dict = {}
        self.random: SystemRandom = rng

        self.map_transfer = [0, 0, 0, 0, 0]
        self.map_transfer_ex = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.monster_book_cover_id = 0

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


@define
class Account(ABCMeta):
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
class PendingLogin(ABCMeta):
    def __init__(self, character: MapleCharacter, account: Account, requested: Any):
        self.character: MapleCharacter
        self.char_id: int
        self.account: Account
        self.requested: Any
        self.migrated: bool
