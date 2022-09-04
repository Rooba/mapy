import asyncio
import signal
from abc import abstractmethod
from asyncio import (
    Event,
    InvalidStateError,
    Lock,
    get_running_loop,
    new_event_loop,
    sleep,
)
from collections import Counter
from datetime import datetime
from inspect import getmembers
from io import BytesIO
from ipaddress import IPv4Address
from pathlib import Path
from socket import AF_INET, IPPROTO_TCP, SOCK_STREAM, TCP_NODELAY, socket
from time import time
from types import new_class
from typing import Any, Coroutine, Literal, TypeAlias

from yaml import Dumper, Loader, YAMLObject, dump, load

from .client import WvsGameClient, WvsLoginClient
from .constants import (
    ANTIREPEAT_BUFFS,
    Config,
    Network,
    WorldFlag,
    Worlds,
    get_job_from_creation,
    is_event_vehicle_skill,
)
from .cpacket import CPacket
from .crypto.maple_iv import MapleIV
from .database.db_client import DatabaseClient
from .game.character import MapleCharacter
from .http_api import http_api
from .logger import Logger
from .opcodes import CRecvOps
from .packet import Packet, PacketHandler, packet_handler
from .scripting import NpcScript

_RetAddress: TypeAlias = tuple[str, int]

global _WvsCenter


class ClientBase:
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
        self._parent: "WvsCenter"
        self._logger: Logger
        self._center: "WvsCenter"

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
    def identifier(self) -> _RetAddress:
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


class World:
    def __init__(self, id):
        self._world = Worlds(id)
        self._channels = []
        self._flag = WorldFlag.New
        self._allow_multi_leveling = Config.ALLOW_MULTI_LEVELING
        self._default_creation_slots = Config.DEFAULT_CREATION_SLOTS
        self._disable_character_creation = False
        self.event_message = Config.DEFAULT_EVENT_MESSAGE
        self.ticker_message = Config.DEFAULT_TICKER
        self.exp_rate = Config.EXP_RATE
        self.quest_exp_rate = Config.QUEST_EXP
        self.party_quest_exp_rate = Config.PARTY_QUEST_EXP
        self.meso_rate = Config.MESO_RATE
        self.drop_rate = Config.DROP_RATE

    @property
    def id(self):
        return self._world.value

    @property
    def name(self):
        return self._world.name

    @property
    def port(self):
        return 8584 + (20 * self._world.value)

    @property
    def population(self):
        return sum([channel.population for channel in self._channels])

    @property
    def channels(self) -> list["WvsGame"]:
        return self._channels

    def add_channel(self, item):
        self._channels.append(item)

    def __getitem__(self, key):
        for channel in self._channels:
            if channel.channel_id == key:
                return channel

        return None


class ChannelConfig(YAMLObject):
    yaml_tag = "!Channel"
    channels = Counter()

    __defaults__ = {
        "rates": {
            "exp": 2.0,
            "meso": 1.0,
            "drop": 1.5,
            "afk_exp": 1.5,
            "active_party_exp": 2.0,
            "quest_exp": 2.0,
            "pq_exp": 1.5,
            "mob_respawn_delay": 1.5,
            "mob_spawn_count": 0.85,
        },
        "combat": {
            "boss_damage": 1.5,
            "boss_defense": 0.8,
            "boss_hp": 2.0,
            "mob_hp": 2.0,
            "mob_damage": 2,
            "boss_exp": 0.7,
            "boss_drop": 1.5,
            "death_exp_loss": 5.0,
        },
        "extra": {
            "ticker_message": "Welcome!",
            "global_npc": False,
            "map_teles": False,
            "hyper_rock_limitations": [18000000000],
            "enabled_events": ["ZakumPQ", "HorntailPQ", "PinkBean"],
        },
        "id": 0,
        "port": 8585,
    }

    def __setstate__(self, state):
        data = ChannelConfig.__defaults__ | state
        data_c = data.copy()
        for k, v in data_c.items():
            self.__setattr__(k, v)
            self.__dict__[k] = v

    def __setitem__(self, key, value):
        self.__setattr__(key, value)
        self.__dict__[key] = value

    def __getitem__(self, key):
        return super().__getattribute__(key)

    def keys(self):
        return self.__dict__.keys()

    def __init__(self, **data):
        for k, v in (self.__defaults__ | data).items():
            self.__dict__[k] = v
            self.__setattr__(k, v)

    def __new__(cls, **data):
        dats = cls.__defaults__ | data
        dats_c = dats.copy()
        for k, v in dats_c.items():
            if isinstance(v, dict):
                dc_cls = new_class(k, (dict, object))
                dc_inst = dc_cls()
                for dict_key_val, dict_val in v.items():
                    setattr(dc_inst, dict_key_val, dict_val)
                    dc_inst[dict_key_val] = dict_val
                dats[k] = dc_inst

        self = super().__new__(cls)
        self.__init__(**dats)
        return self

    @classmethod
    def to_yaml(cls, dumper: Dumper, data):
        mappings = {}
        for k, v in cls.__defaults__.items():
            if isinstance(v, (int, str)):
                mappings[k] = data[k] if k in data else v
            if k in cls.__defaults__ and isinstance(v, dict):
                mappings[k] = {}
                for kk, vv in v.items():
                    mappings[k][kk] = data[k][kk] if kk in data[k] else vv
            else:
                continue
        mappings["port"] = data["port"]
        mappings["id"] = data["id"]
        n = new_class("ChannelConfig", (dict, ChannelConfig, YAMLObject))
        nn = n()
        nn.__dict__ = mappings
        return dumper.represent_yaml_object("!Channel", nn, cls)

    def __getattribute__(self, __name: str) -> Any:
        return super(ChannelConfig, self).__getattribute__(__name)

    def __iter__(self):
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("__")
        }.__iter__()

    def __get__(self, key):
        return getattr(self, key, None)

    @property
    def world(self) -> Worlds:
        return self.__getattribute__("__world")

    @property
    def world_id(self):
        return self.world.value

    @world.setter
    def world(self, value):
        setattr(self, "__world", value)
        self.__dict__["__world"] = value

    @property
    def world_name(self):
        return self.world.name

    @property
    def drop(self):
        return self.rates.drop  # type: ignore

    @property
    def exp(self):
        return self.rates.exp  # type: ignore

    @property
    def meso(self):
        return self.rates.meso  # type: ignore

    @property
    def death_penalty(self):
        return self.combat.death_exp_loss  # type: ignore

    @property
    def ticker_message(self):
        return self.extra.ticker_message  # type: ignore

    @property
    def mob_damage(self):
        return self.combat.mob_damage  # type: ignore

    @property
    def mob_health(self):
        return self.combat.mob_hp  # type: ignore

    @property
    def mob_respawn(self):
        return self.combat.mob_respawn_delay  # type: ignore


class WvsCenter:
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

    RUNNING = Event()

    def __init__(self):
        self._name = "<lc>Server Core</lc>"
        self._loop = new_event_loop()
        self._clients = set()
        self._pending_logins = []
        self._login = None
        self._config = {}
        self._start_time = int(time())
        self._shop = None
        self._worlds = {}
        self._logger = Logger(self)
        self._load_config()

    @property
    def pending_logins(self):
        return self._pending_logins

    @property
    def data(self) -> "DatabaseClient":
        return NotImplemented

    @property
    def login(self) -> "WvsLogin | None":
        return self._login

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def shop(self) -> "WvsShop | None":
        return self._shop

    @shop.setter
    def shop(self, shop):
        self._shop = shop

    @property
    def worlds(self) -> dict[int, World]:
        return self._worlds

    def log(self, message) -> None:
        self.logger.log_basic(message)

    def _load_config(self):
        if not Path("config_test.yaml").exists():
            self._make_config()

        else:
            doc = open("config_test.yaml", "r")
            self._config = load(doc, Loader)
            doc.close()

    def _make_config(self):
        self._config = {
            "database": {
                "host": "127.0.0.1",
                "port": 5432,
                "user": "postgres",
                "password": "smoqueed420",
                "database": "mapy",
            },
            "game": {
                "worlds": [
                    {
                        "id": w.value,
                        "name": w.name.lower(),
                        "channels": [
                            ChannelConfig(id=c, port=9494 + (c + (w.value * 20)))
                            for c in range(Network.CHANNEL_COUNT)
                        ],
                    }
                    for w in Network.ACTIVE_WORLDS
                ]
            },
        }
        self.save_config()

    def save_config(self):
        with open("config_test.yaml", "w") as f:
            dump(self._config, f, default_flow_style=False, width=88)

    def _run(self):
        if self.RUNNING.is_set():
            return

        loop = self._loop
        try:
            loop.add_signal_handler(signal.SIGINT, self._loop.stop)
            loop.add_signal_handler(signal.SIGTERM, self._loop.stop)
        except NotImplementedError:
            pass

        def stop_loop_on_completion(f):
            loop.stop()

        future = loop.create_task(self._start())
        future.add_done_callback(stop_loop_on_completion)

        try:
            loop.run_forever()

        except KeyboardInterrupt:
            self.log("Received signal to terminate event loop")
            # loop.run_until_complete(self.data.stop())

        finally:
            future.remove_done_callback(stop_loop_on_completion)
            self.save_config()
            loop.run_until_complete(self._loop.shutdown_asyncgens())
            self.log(f"Closed {self._name}")

    async def _start(self):
        self.RUNNING.set()
        self._start_time = int(time())
        self.log("Initializing Server")

        self._login = WvsLogin()
        await self._login.run()

        # world_id = Worlds.SCANIA.value

        for _world in self._config["game"]["worlds"]:
            world_enum = Worlds(_world["id"])
            world = World(world_enum.value)

            for channel_config in _world["channels"]:
                channel_config.world = world_enum
                channel = WvsGame(**channel_config)
                await channel.run()
                world.add_channel(channel)

            self.worlds[world_enum.value] = world

        async def startup():
            http_api.ctx.center = _WvsCenter
            http = await http_api.create_server(
                host="127.0.0.1",
                port=12345,
                noisy_exceptions=True,
                return_asyncio_server=True,
                debug=True,
            )
            if http:
                await http.startup()

        self._loop.create_task(startup())

        while get_running_loop().is_running():
            await sleep(600.0)

    @property
    def uptime(self):
        return int(time()) - self._start_time

    @property
    def population(self):
        login_population = 0
        if self._login:
            login_population += self._login.population

        return sum(w.population for _, w in self.worlds.items()) + login_population


class ServerBase:
    """Server base for center, channel, and login servers"""

    __slots__ = (
        "_name",
        "_clients",
        "_port",
        "_packet_handlers",
        "_ready",
        "_serv_sock",
        "_acceptor",
        "_logger",
        "_loop",
        "_alive",
        "_center",
    )

    def __init__(self):
        self._name = ""
        self._loop = get_running_loop()
        self._logger: Logger = Logger(self)
        self._clients = []
        self._packet_handlers = []
        self._ready = Event()
        if not self._port:
            self._port = 9494

        self._alive = Event()
        self._acceptor = None
        self._serv_sock = socket(AF_INET, SOCK_STREAM)
        self._serv_sock.setblocking(False)
        self._serv_sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        self._serv_sock.bind(("127.0.0.1", self._port))
        self._serv_sock.listen(0)
        self.add_packet_handlers()

    @property
    def center(self) -> WvsCenter | None:
        if not _WvsCenter:
            return None
        return _WvsCenter

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    def log(self, message, level=None):
        if not self._logger:
            return

        if not level:
            return self._logger.log_basic(message)
        else:
            return self._logger.log(str(level).upper(), message)

    @abstractmethod
    async def client_connect(self, client_sock) -> ClientBase:
        return NotImplemented

    @property
    def alive(self) -> bool:
        return self._alive.is_set()

    async def run(self):
        self._alive.set()
        self._ready.set()
        self._acceptor = self._loop.create_task(self.listen())

    def close(self) -> None:
        if self._acceptor:
            self._acceptor.cancel()
        else:
            raise InvalidStateError(
                "The acceptor is not currently running or accepting connections."
            )

    async def on_client_accepted(self, socket: socket):
        if not _WvsCenter:
            return

        client = await self.client_connect(socket)

        if not client:
            self.log(f"socket ({socket.getpeername}) connecting failed.")
            return

        self.log(f"{self.name} Accepted <lg>{client.ip}</lg>")

        _WvsCenter._clients.add(client)
        self._clients.append(client)

        # Dispatch accept packet to client and begin client socket loop
        await client.initialize()

    async def on_client_disconnect(self, client):
        self._clients.remove(client)

        self.log(f"Client Disconnected {client.ip}")

    def add_packet_handlers(self):
        members = getmembers(self)
        for _, member in members:
            # Register all packet handlers for inheriting server
            if (
                isinstance(member, PacketHandler)
                and member not in self._packet_handlers
            ):
                self._packet_handlers.append(member)

    def wait_until_ready(self) -> Coroutine[Any, Any, Literal[True]]:
        """Block event loop until the GameServer has started listening for clients."""
        return self._ready.wait()

    async def listen(self):
        self.log(f"Listening on port <lr>{self._port}</lr>", "info")

        while self._alive.is_set():
            client_sock, _ = await self._loop.sock_accept(self._serv_sock)
            client_sock.setblocking(False)
            client_sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
            self._loop.create_task(self.on_client_accepted(client_sock))

    @property
    def data(self):
        if _WvsCenter:
            return _WvsCenter.data

    @property
    def name(self) -> str:
        return self._name

    @property
    def population(self) -> int:
        return len(self._clients)

    def push(self, client: ClientBase, packet: Packet):
        self._logger.log_ipkt(
            f"{self.name} {packet.name} {client.ip} {packet.to_string()}"
        )

        for __packet_handler in self._packet_handlers:
            if __packet_handler.op_code == packet.op_code:
                get_running_loop().create_task(
                    packet_handler.callback(self, client, packet)
                )
                break
        else:
            self.log(
                f"{self.name} Unhandled event in : <w>{packet.name}</w>", "WARNING"
            )


class WvsGame(ServerBase, ChannelConfig):
    def __new__(cls, **data):
        self = super().__new__(cls, **data)
        return self

    def __init__(self, **data):
        for k, v in data.items():
            setattr(self, k, v)

        self.channels.update([self.world.value])
        self.channel_id = self.id
        self._field_manager = {}
        super().__init__()

    async def client_connect(self, client):
        if not _WvsCenter:
            return

        game_client = WvsGameClient(self, client)
        _WvsCenter._clients.append(game_client)  # type: ignore
        return game_client

    async def on_client_disconnect(self, client):
        if not _WvsCenter:
            return

        if client.logged_in:
            field = await client.get_field()
            field.clients.remove(client)
            # field.sockets.pop(client.character)
            await field.broadcast(CPacket.user_leave_field(client.character))

        _WvsCenter._clients.remove(client)
        await super().on_client_disconnect(client)

    async def get_field(self, field_id):
        if not _WvsCenter or not self.data:
            return

        field = self._field_manager.get(field_id, None)
        if field:
            return field

        field = await self.data.field.get(field_id)
        self._field_manager[field_id] = field

        return field

    @packet_handler(CRecvOps.CP_MigrateIn)
    async def handle_migrate_in(self, client, packet):
        if not _WvsCenter or not self.data:
            return

        uid = packet.decode_int()
        packet.decode_buffer(16)  # Machine ID
        packet.decode_byte()  # is gm
        packet.decode_byte()
        packet.decode_long()  # Session ID

        login_req: PendingLogin | None

        for x in _WvsCenter._pending_logins:
            if x.character.id == uid:
                login_req = x
                break

        else:
            login_req = None

        if not login_req:
            return await client.disconnect()

        login_req.migrated = True
        login_req.character._client = client

        client.character = await self.data.characters.load(uid, client)
        field = await self.get_field(client.character.field_id)
        if not field:
            return

        await field.add(client)

        await client.send_packet(CPacket.claim_svr_changed(True))
        await client.send_packet(CPacket.set_gender(client.character.stats.gender))
        await client.send_packet(CPacket.func_keys_init(client.character.func_keys))
        await client.send_packet(CPacket.broadcast_server_msg(self.ticker_message))

    @packet_handler(CRecvOps.CP_UserMove)
    async def handle_user_move(self, client, packet):
        packet.decode_long()  # v1
        packet.decode_byte()  # portal count
        packet.decode_long()  # v2
        packet.decode_int()  # map crc
        packet.decode_int()  # key
        packet.decode_int()  # key crc

        move_path = packet.decode_buffer(-1)
        client.character.position.decode_move_path(move_path)
        await client.broadcast(CPacket.user_movement(client.character.id, move_path))

    @packet_handler(CRecvOps.CP_UserSkillUseRequest)
    async def handle_skill_use_request(self, client, packet):
        packet.decode_int()  # tick count
        skill_id = packet.decode_int()
        _ = packet.decode_byte()

        if skill_id in ANTIREPEAT_BUFFS:
            packet.decode_short()  # x
            packet.decode_short()  # y

        if skill_id == 4131006:
            packet.decode_int()

        if is_event_vehicle_skill(skill_id):
            packet.skip(1)
            if skill_id == 2311001:
                packet.skip(2)

        packet.decode_short()

        casted = False
        if skill_id:
            casted = await client.character.skills.cast(skill_id)

        await client.send_packet(CPacket.enable_actions())

        if casted:
            client.broadcast(
                CPacket.effect_remote(
                    client.character.obj_id,
                    1,
                    skill_id,
                    client.character.stats.level,
                    1,
                )
            )

    @packet_handler(CRecvOps.CP_UserSelectNpc)
    async def handle_user_select_npc(self, client, packet):
        obj_id = packet.decode_int()
        packet.decode_short()  # x
        packet.decode_short()  # y

        if client.npc_script:
            ...  # client has npc script already?

        npc = client.character.field.npcs.get(obj_id)

        if npc:
            client.npc_script = NpcScript.get_script(npc.id, client)
            await client.npc_script.execute()

    @packet_handler(CRecvOps.CP_UserScriptMessageAnswer)
    async def handle_user_script_message_answer(self, client, packet):
        script = client.npc_script

        type_ = packet.decode_byte()
        type_expected = script.last_msg_type

        if type_ != type_expected:
            self.log(
                f"User answered type: [{type_}], expected [{type_expected}]" "debug"
            )
            return

        resp = packet.decode_byte()
        self.log(f"Script response: [{resp}]")

        if type_ == 0:
            if resp == 255:
                script.end_chat()
            elif resp == 0:
                await script.proceed_back()
            elif resp == 1:
                await script.proceed_next(resp)

    @packet_handler(CRecvOps.CP_UpdateGMBoard)
    async def handle_update_gm_board(self, client, packets):
        ...

    @packet_handler(CRecvOps.CP_RequireFieldObstacleStatus)
    async def handle_require_field_obstacle(self, client, packets):
        ...


class PendingLogin:
    def __init__(self, character, account, requested):
        self.character = character
        self.char_id = character.id
        self.account = account
        self.requested = requested
        self.migrated = False


class WvsLogin(ServerBase):
    def __init__(self):
        self.port = Network.LOGIN_PORT
        super().__init__()
        self._worlds = []
        self._auto_register = Config.AUTO_REGISTER
        self._request_pin = Config.REQUEST_PIN
        self._request_pic = Config.REQUEST_PIC
        self._require_staff_ip = Config.REQUIRE_STAFF_IP
        self._max_characters = Config.MAX_CHARACTERS
        self._login_pool = []

    def add_world(self, world):
        self._worlds.append(world)

    async def client_connect(self, client):
        return WvsLoginClient(self, client)

    @packet_handler(CRecvOps.CP_CreateSecurityHandle)
    async def create_secuirty_heandle(self, client, packet):
        if Config.AUTO_LOGIN:
            packet = Packet(op_code=CRecvOps.CP_CheckPassword)
            packet.encode_string("admin")
            packet.encode_string("admin")
            packet.seek(2)
            client.dispatch(packet)

    @packet_handler(CRecvOps.CP_CheckPassword)
    async def check_password(self, client, packet):
        password = packet.decode_string()
        username = packet.decode_string()
        response = await client.login(username, password)

        if response == 0:
            return await client.send_packet(
                CPacket.check_password_result(client, response)
            )

        await client.send_packet(CPacket.check_password_result(response=response))

    async def send_world_information(self, client) -> None:
        for world in _WvsCenter.worlds:
            await client.send_packet(CPacket.world_information(world))

        await client.send_packet(CPacket.end_world_information())
        await client.send_packet(CPacket.last_connected_world(0))

        await client.send_packet(CPacket.send_recommended_world(self._worlds))

    @packet_handler(CRecvOps.CP_WorldRequest)
    async def world_request(self, client, packet):
        await self.send_world_information(client)

    @packet_handler(CRecvOps.CP_WorldInfoRequest)
    async def world_info_request(self, client, packet):
        await self.send_world_information(client)

    @packet_handler(CRecvOps.CP_CheckUserLimit)
    async def check_user_limit(self, client, packet):
        await client.send_packet(CPacket.check_user_limit(0))

    @packet_handler(CRecvOps.CP_SelectWorld)
    async def select_world(self, client, packet):
        packet.decode_byte()

        client.world_id = world_id = packet.decode_byte()
        client.channel_id = packet.decode_byte()

        client.account.last_connected_world = world_id

        # Load avatars for specific world in future
        await client.load_avatars(world_id=world_id)
        await client.send_packet(CPacket.world_result(client.avatars))

    @packet_handler(CRecvOps.CP_LogoutWorld)
    async def logout_world(self, client, packet):
        pass

    @packet_handler(CRecvOps.CP_CheckDuplicatedID)
    async def check_duplicated_id(self, client, packet):
        name = packet.decode_string()
        exists = await _WvsCenter.data.characters.get(name=name) is not None

        await client.send_packet(CPacket.check_duplicated_id_result(name, exists))

    @packet_handler(CRecvOps.CP_ViewAllChar)
    async def view_all_characters(self, client, packet):
        await client.load_avatars()
        packet.decode_byte()  # game_start_mode

        await asyncio.sleep(2)
        await client.send_packet(CPacket.start_view_all_characters(client.avatars))

        for world in _WvsCenter.worlds:
            await client.send_packet(CPacket.view_all_characters(world, client.avatars))

    @packet_handler(CRecvOps.CP_CreateNewCharacter)
    async def create_new_character(self, client, packet):
        character = MapleCharacter()
        character.stats.name = packet.decode_string()
        character.stats.job = get_job_from_creation(packet.decode_int())
        character.stats.sub_job = packet.decode_short()
        character.stats.face = packet.decode_int()
        character.stats.hair = packet.decode_int() + packet.decode_int()
        character.stats.skin = packet.decode_int()

        invs = character.inventories

        top = await _WvsCenter.data.items.get(packet.decode_int())
        bottom = await _WvsCenter.data.items.get(packet.decode_int())
        shoes = await _WvsCenter.data.items.get(packet.decode_int())
        weapon = await _WvsCenter.data.items.get(packet.decode_int())

        invs.add(top, slot=-5)
        invs.add(bottom, slot=-6)
        invs.add(shoes, slot=-7)
        invs.add(weapon, slot=-11)

        character.stats.gender = packet.decode_byte()

        character_id = await _WvsCenter.data.account(
            id=client.account.id
        ).create_character(character)

        if character_id:
            character.stats.id = character_id
            client.avatars.append(character)

            return await client.send_packet(
                CPacket.create_new_character(character, False)
            )

        return await client.send_packet(CPacket.create_new_character(character, True))

    @packet_handler(CRecvOps.CP_SelectCharacter)
    async def select_character(self, client, packet):
        if not _WvsCenter:
            return

        uid = packet.decode_int()
        character = next((c for c in client.avatars if c.id == uid), None)
        channel = _WvsCenter.worlds[client.world_id][client.channel_id]
        if not channel:
            return

        port = channel.port

        _WvsCenter.pending_logins.append(
            PendingLogin(character, client.account, datetime.now())
        )

        await client.send_packet(CPacket.select_character_result(uid, port))


class WvsShop(ServerBase):
    def __init__(self):
        pass


if (
    not locals().get("_WvsCenter", None)
    and not globals().get("_WvsCenter", None)
    and not WvsCenter.RUNNING.is_set()
):
    _WvsCenter = WvsCenter()
    _WvsCenter._run()
