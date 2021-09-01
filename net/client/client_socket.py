from io import BytesIO
from random import randint
from socket import SHUT_RD
from time import time

from utils.tools import to_string
from asyncio import create_task, Lock, get_event_loop

from common.constants import VERSION, SUB_VERSION, LOCALE
from net.packets.crypto import MapleIV, MapleAes, shanda
from net.packets.packet import Packet


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
                m_recv_buffer = await self._loop.sock_recv(self._socket, self.recieve_size)
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
                        self._overflow = m_recv_buffer[length + 4:]
                        m_recv_buffer = m_recv_buffer[:length + 4]

                    m_recv_buffer = self.manipulate_buffer(m_recv_buffer)

            client.dispatch(Packet(m_recv_buffer))

    async def send_packet(self, out_packet):
        packet_length = len(out_packet)
        packet = bytearray(out_packet.getvalue())

        buf = packet[:]

        final_length = packet_length + 4
        final = bytearray(final_length)
        async with self._lock:
            MapleAes.get_header(final, self.m_siv, packet_length, VERSION)
            buf = shanda.encrypt_transform(buf)
            final[4:] = MapleAes.transform(buf, self.m_siv)

        await self._loop.sock_sendall(self._socket, final)

    async def send_packet_raw(self, packet):
        await self._loop.sock_sendall(self._socket, packet.getvalue())

    def manipulate_buffer(self, buffer):
        buf = bytearray(buffer)[4:]

        buf = MapleAes.transform(buf, self.m_riv)
        buf = shanda.decrypt_transform(buf)

        return buf
