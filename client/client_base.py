from asyncio import create_task, Lock, get_event_loop
from random import randint
import logging

log = logging.getLogger(__name__)

from common.constants import VERSION, SUB_VERSION, LOCALE
from net.client.client_socket import ClientSocket
from net.packets.crypto import MapleIV
from net.packets.packet import Packet
import server

class ClientBase:
    def __init__(self, parent, socket):
        self.m_socket = socket
        self._parent = parent
        self._port = None

    async def initialize(self):
        
        if not isinstance(self._parent, server.CenterServer):
            self.m_socket.m_siv = MapleIV(100)
            self.m_socket.m_riv = MapleIV(50)

            with Packet(op_code=0x0E) as packet:
                packet.encode_short(VERSION)
                packet.encode_string(SUB_VERSION)
                packet.encode_int(int(self.m_socket.m_riv))
                packet.encode_int(int(self.m_socket.m_siv))
                packet.encode_byte(LOCALE)

                await self.send_packet_raw(packet)

        self._receive_task = self._parent._loop.create_task(self.receive())

    async def receive(self):
        self._is_alive = True

        try:
            while self._is_alive:
                m_recv_buffer = await self.sock_recv()

                if not m_recv_buffer:
                    await self._parent.on_client_disconnect(self)
                    return

                if self.m_socket.m_riv:
                    m_recv_buffer = self.manipulate_buffer(m_recv_buffer)

                self.dispatch(Packet(m_recv_buffer, op_codes=self._parent.__opcodes__))

        except ConnectionResetError:
            await self._parent.on_client_disconnect(self)

    def dispatch(self, packet):
        self._parent.dispatcher.push(self, packet)

    async def sock_recv(self):
        return await self.m_socket.sock_recv()

    async def send_packet(self, packet):
        op_code = packet.op_code

        log.debug(f"Sent : [{op_code.name}] {packet.to_string()}")

        await self.m_socket.send_packet(packet)

    async def send_packet_raw(self, packet):
        log.debug(f"Sent : [{packet.op_code}] {packet.to_string()}")
        await self.m_socket.send_packet_raw(packet)

    def manipulate_buffer(self, buffer):
        return self.m_socket.manipulate_buffer(buffer)