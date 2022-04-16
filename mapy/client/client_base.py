from asyncio import Lock, get_event_loop
from random import randint

from .. import log
from ..common.constants import LOCALE, SUB_VERSION, VERSION
from ..net.crypto import MapleAes, MapleIV, decrypt_transform, encrypt_transform
from ..net.packet import Packet


class ClientSocket:
    def __init__(self, socket):
        self._loop = get_event_loop()
        self._socket = socket
        self._lock = Lock()
        self.recieve_size = 16384
        self.m_riv = None
        self.m_siv = None
        self._is_alive = False
        self._overflow = None

    @property
    def identifier(self):
        return self._socket.getpeername()

    def close(self):
        return self._socket.close()

    async def receive(self, client):
        self._is_alive = True
        while self._is_alive:
            if not self._overflow:
                m_recv_buffer = await self._loop.sock_recv(
                    self._socket, self.recieve_size
                )
                if not m_recv_buffer:
                    await client._parent.on_client_disconnect(client)
                    return

            else:
                m_recv_buffer = self._overflow
                self._overflow = None

            if self.m_riv:
                async with self._lock:
                    length = MapleAes.get_length(m_recv_buffer)
                    if length != len(m_recv_buffer) - 4:
                        self._overflow = m_recv_buffer[length + 4 :]
                        m_recv_buffer = m_recv_buffer[: length + 4]

                    m_recv_buffer = self.manipulate_buffer(m_recv_buffer)

            client.dispatch(Packet(m_recv_buffer))

    async def send_packet(self, out_packet):
        packet_length = len(out_packet)
        packet = bytearray(out_packet.getvalue())

        buf = packet[:]

        final = bytearray(packet_length + 4)
        async with self._lock:
            MapleAes.get_header(final, self.m_siv, packet_length, VERSION)
            buf = encrypt_transform(buf)
            final[4:] = MapleAes.transform(buf, self.m_siv)

        await self._loop.sock_sendall(self._socket, final)

    async def send_packet_raw(self, packet):
        await self._loop.sock_sendall(self._socket, packet.getvalue())

    def manipulate_buffer(self, buffer):
        buf = bytearray(buffer)[4:]

        buf = MapleAes.transform(buf, self.m_riv)
        buf = decrypt_transform(buf)

        return buf


class ClientBase:
    def __init__(self, parent, socket):
        self.m_socket = socket
        self._parent = parent
        self.port = None
        self._is_alive = False

        self.logged_in = False
        self.world_id = None
        self.channel_id = None

    async def initialize(self):
        self.m_socket.m_siv = MapleIV(randint(0, 2**31 - 1))
        self.m_socket.m_riv = MapleIV(randint(0, 2**31 - 1))

        packet = Packet(op_code=0x0E)
        packet.encode_short(VERSION)
        packet.encode_string(SUB_VERSION)
        packet.encode_int(self.m_socket.m_riv.value)
        packet.encode_int(self.m_socket.m_siv.value)
        packet.encode_byte(LOCALE)

        await self.send_packet_raw(packet)

        await self.m_socket.receive(self)

    def dispatch(self, packet):
        self._parent.dispatcher.push(self, packet)

    async def send_packet(self, packet):
        log.packet(f"{packet.name} {self.ip} {packet.to_string()}", "out")

        await self.m_socket.send_packet(packet)

    async def send_packet_raw(self, packet):
        log.packet(f"{packet.name} {self.ip} {packet.to_string()}", "out")

        await self.m_socket.send_packet_raw(packet)

    @property
    def parent(self):
        return self._parent

    @property
    def ip(self):
        return self.m_socket.identifier[0]

    @property
    def data(self):
        return self._parent.data
