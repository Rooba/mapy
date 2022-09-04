from asyncio import Lock, get_running_loop
from random import randint
from typing import Any

from .constants import Config, Worlds
from .crypto import MapleAes, MapleIV, decrypt_transform, encrypt_transform
from .logger import Logger
from .packet import Packet

RECV_SIZE = 4096


class ClientBase:
    __slots__ = (
        "_socket",
        "_port",
        "_overflow_buff",
        "_recv_buff",
        "_logged_in",
        "_world_id",
        "_channel_id",
        "_lock",
        "_m_riv",
        "_m_siv",
        "_parent",
        "_logger",
        "_center",
    )

    def __init__(self, parent, socket):
        self._socket = socket
        self._parent = self._center = parent

        self._port = None
        self._overflow_buff = bytearray(1024)
        self._recv_buff = bytearray(1024)
        self._logged_in = False
        self._world_id = 0
        self._lock = Lock()
        self._m_riv = None
        self._m_siv = None
        self._logger = Logger(f"<lc>Client ({self.ip})</lc>")

    @property
    def connected_channel(self):
        return self._center.worlds[self._world_id].channels[self._channel_id]

    @property
    def ip(self):
        return self._socket.getpeername()[0]

    @property
    def data(self):
        return self._parent.data

    @property
    def identifier(self):
        return self._socket.getpeername()

    def dispatch(self, packet):
        self._parent.push(self, packet)

    def close(self):
        return self._socket.close()

    async def initialize(self):
        self._m_siv = MapleIV(randint(0, 1 << 31))
        self._m_riv = MapleIV(randint(0, 1 << 31))

        packet = Packet(op_code=0x0E)
        packet.encode_short(Config.VERSION)
        packet.encode_string(Config.SUB_VERSION)
        packet.encode_int(self._m_riv.value)
        packet.encode_int(self._m_siv.value)
        packet.encode_byte(Config.LOCALE)

        await self.send_packet_raw(packet)

        while get_running_loop().is_running():

            if not self._overflow_buff:
                await get_running_loop().sock_recv_into(
                    self._socket, memoryview(self._recv_buff)[:]
                )

                if not self._recv_buff:
                    await self._parent.on_client_disconnect(self)
                    return

            else:
                self._recv_buff = self._overflow_buff
                self._overflow_buff = bytearray()

            if self._m_riv:
                async with self._lock:
                    length = MapleAes.get_length(self._recv_buff)
                    if length != len(self._recv_buff) - 4:
                        self._overflow_buff = self._recv_buff[length + 4 :]
                        self._recv_buff = self._recv_buff[: length + 4]

                    self._recv_buff = self.manipulate_buffer(self._recv_buff)

            self.dispatch(Packet(data=self._recv_buff))
            self._recv_buff = bytearray()

    async def send_packet(self, out_packet):
        self._logger.log_opkt(f"{out_packet.to_string()}")

        packet_length = len(out_packet)
        packet = bytearray(out_packet.getvalue())

        buf = packet[:]

        final = bytearray(packet_length + 4)
        async with self._lock:
            MapleAes.get_header(final, self._m_siv, packet_length, Config.VERSION)
            buf = encrypt_transform(buf)
            final[4:] = MapleAes.transform(buf, self._m_siv)

        await get_running_loop().sock_sendall(self._socket, final)

    async def send_packet_raw(self, packet):
        self._logger.log_opkt(f"{packet.name} {self.ip} {packet.to_string()}")

        await get_running_loop().sock_sendall(self._socket, packet.getvalue())

    def manipulate_buffer(self, buffer):
        buf = bytearray(buffer)[4:]

        buf = MapleAes.transform(buf, self._m_riv)
        buf = decrypt_transform(buf)

        return buf


class WvsLoginClient(ClientBase):
    """LoginClient

    Parameters
    ----------

    parent: :class:`ServerBase`
        Parent server client is connecting to
    socket: :class:`Socket`
        Socket holding client - server connection
    name: str
        Name identifying type of client
    """

    def __init__(self, parent, socket):
        super().__init__(parent, socket)

        self._account = None
        self._avatars = []

    async def login(self, username, password):
        resp, account = await (
            self.data.account(username=username, password=password).login()
        )

        if not resp:
            self._account = account
            self._logged_in = True
            return 0

        return resp

    async def load_avatars(self, world_id=None):
        if not self._account:
            self._avatars = []
            return

        self._avatars = await (
            self.data.account(id=self._account.id).get_entries(world_id=world_id)
        )

    @property
    def account_id(self):
        return getattr(self._account, "id", -1)


class WvsGameClient(ClientBase):
    def __init__(self, parent, socket):
        super().__init__(parent, socket)

        self._channel_id = parent.channel_id
        self._world_id = 0
        self._character: Any | None = None
        self._npc_script = None
        self._sent_char_data = False

    @property
    def world_id(self):
        if not self._logged_in:
            return -1

        return self._world_id or -1

    @world_id.setter
    def world_id(self, value):
        if isinstance(value, Worlds):
            self._world_id = value._value_
        elif isinstance(value, int):
            self._world_id = value
        else:
            raise ValueError()

    async def broadcast(self, packet):
        if not self._character:
            return

        await self._character.field.broadcast(packet, self)

    def get_field(self):
        if not self._character:
            return

        return self.connected_channel.get_field(self._character.field_id)
