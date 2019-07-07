import asyncio
from socket import socket, SOCK_STREAM, AF_INET

from common.constants import SECRET_KEY, WORLD_COUNT
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

        self._loop.create_task(self.create_connection())

    async def create_connection(self):
        await self._loop.sock_connect(self._socket, (self._host, self._port))

        self._loop.create_task(self.loop())

        with Packet(op_code=InterOps.RegistrationRequest) as out_packet:
            out_packet.encode_byte(ServerType.channel)
            out_packet.encode_string(SECRET_KEY)
            
            await self.send_packet_raw(out_packet)

    async def loop(self):
        while self._parent.is_alive:
            m_recv_buffer = await self.sock_recv()

            if m_recv_buffer == b'':
                self._parent.is_alive = False
                return

            self.dispatch(Packet(data = m_recv_buffer, op_codes=InterOps))

    async def sock_recv(self):
        return await self._loop.sock_recv(self._socket, 16384)

    def dispatch(self, packet):
        self._parent._dispatcher.push(self._socket, packet)

    async def send_packet_raw(self, packet):
        await self._loop.sock_sendall(self._socket, packet.getvalue())