import server
from net.packets.packet import Packet
from net.packets.crypto import MapleIV
from net.client.client_socket import ClientSocket
from common.constants import VERSION, SUB_VERSION, LOCALE
from asyncio import create_task
from random import randint
from loguru import logger


class ClientBase:
    def __init__(self, parent, socket):
        self.m_socket = socket
        self._parent = parent
        self.port = None
        self._is_alive = False

    async def initialize(self):

        if not isinstance(self._parent, server.CenterServer):
            self._parent._loop.create_task(self.receive())

            # self.m_socket.m_siv = MapleIV(randint(0, 2**31-1))
            self.m_socket.m_siv = MapleIV(100)
            # self.m_socket.m_riv = MapleIV(randint(0, 2**31-1))
            self.m_socket.m_riv = MapleIV(50)

            packet = Packet(op_code=0x0E)
            packet.encode_short(VERSION)
            packet.encode_string(SUB_VERSION)
            packet.encode_int(self.m_socket.m_riv.value)
            packet.encode_int(self.m_socket.m_siv.value)
            packet.encode_byte(LOCALE)

            return await self.send_packet_raw(packet)

        self._parent._loop.create_task(self.receive())

    async def receive(self):
        self._is_alive = True

        while self._is_alive:
            m_recv_buffer = await self.sock_recv()

            if not m_recv_buffer:
                await self._parent.on_client_disconnect(self)
                return

            if self.m_socket.m_riv:
                m_recv_buffer = self.manipulate_buffer(m_recv_buffer)

            self.dispatch(
                Packet(m_recv_buffer, op_codes=self._parent.__opcodes__))

    def dispatch(self, packet):
        self._parent.dispatcher.push(self, packet)

    async def sock_recv(self):
        return await self.m_socket.sock_recv()

    async def send_packet(self, packet):
        logger.packet(f"{packet.name} {self.ip} {packet.debug_string}", "out")

        await self.m_socket.send_packet(packet)

    async def send_packet_raw(self, packet):
        logger.packet(f"{packet.name} {self.ip} {packet.debug_string}", "out")

        await self.m_socket.send_packet_raw(packet)

    def manipulate_buffer(self, buffer):
        return self.m_socket.manipulate_buffer(buffer)

    @property
    def ip(self):
        return self.m_socket.identifier[0]

    @property
    def data(self):
        return self._parent.data
