import asyncio
from socket import socket, SOCK_STREAM, AF_INET
import logging

log = logging.getLogger(__name__)

from common.enum import ServerType
from net.packets.packet import Packet
from net.packets.opcodes import InterOps

class CenterServer:
    def __init__(self, parent, host, port):
        self._parent = parent
        self._host = host
        self._port = port
        self._loop = parent._loop
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.setblocking(0)
        self.is_alive = True

        self._loop.create_task(self.create_connection())

    async def create_connection(self):
        await self._loop.sock_connect(self._socket, (self._host, self._port))

        self._loop.create_task(self.receive())

        with Packet(op_code=InterOps.RegistrationRequest) as out_packet:
            out_packet.encode_byte(ServerType.login)
            out_packet.encode_string(self._parent._security_key)
            out_packet.encode_byte(len(self._parent._worlds))
            
            for world in self._parent._worlds:
                out_packet.encode_byte(world.id)
                out_packet.encode_string(world.name)
                out_packet.encode_byte(1)
                out_packet.encode_string(world.ticker_message)
                out_packet.encode_byte(world._allow_multi_leveling)
                out_packet.encode_int(world.exp_rate)
                out_packet.encode_int(world.quest_exp_rate)
                out_packet.encode_int(world.party_quest_exp_rate)
                out_packet.encode_int(world.meso_rate)
                out_packet.encode_int(world.drop_rate)

            await self.send_packet_raw(out_packet)

    async def receive(self):
        while self.is_alive:
            m_recv_buffer = await self.sock_recv()

            if not m_recv_buffer:
                self.is_alive = False
                continue

            self.dispatch(Packet(data=m_recv_buffer, op_codes=InterOps))

    async def sock_recv(self):
        return await self._loop.sock_recv(self._socket, 16384)

    def dispatch(self, packet):
        self._parent.dispatcher.push(self._socket, packet)

    async def send_packet_raw(self, packet):
        await self._loop.sock_sendall(self._socket, packet.getvalue())