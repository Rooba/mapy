from random import randint

from asyncio import create_task, Lock, get_event_loop

from common.constants import VERSION, SUB_VERSION, LOCALE
from net.packets.crypto import MapleCryptograph, MapleIV
from net.packets.packet import Packet

class ClientSocket:
    def __init__(self, socket):
        self._loop = get_event_loop()
        self._socket = socket
        self._lock = Lock()

        # create_task(self.listen_packets())
    
    @property
    def identifier(self):
        return self._socket.getpeername()


    # def dispatch(self, packet):
    #     self._server._dispatcher.push(self, packet)

    # async def initialize(self, server, crypto):
    #     self._server = server

    #     if isinstance(crypto, MapleCryptograph):

    #         self.m_siv = MapleIV(randint(0, 2**31-1))
    #         self.m_riv = MapleIV(randint(0, 2**31-1))

    #         packet = Packet(op_code=0X0E)
    #         packet.encode_short(VERSION)
    #         packet.encode_string(SUB_VERSION)
    #         packet.encode_int(self.m_siv)
    #         packet.encode_int(self.m_riv)
    #         packet.encode_byte(LOCALE)

    #         await self.send_packet_raw(packet)

    #     await self.recieve()

    # async def recieve(self):
    #     m_recvBuffer = await self.sock_recv()

    #     if self.m_riv:
    #         m_recvBuffer = self.manipulate_buffer(m_recvBuffer, self.m_riv)

    #     self.dispatch(Packet(m_recvBuffer, op_codes=self._server.__opcodes__))

    async def sock_recv(self):
        return await self._loop.sock_recv(self._socket, 16384)

    async def send_packet(self, packet):
        
        # TODO: Do this
        pass

    async def send_packet_raw(self, packet):
        await self._loop.sock_sendall(self._socket, packet.getvalue())

    # def manipulate_buffer(self, buffer, iv):
    #     return self._server.__crypto__.transform(buffer, iv)