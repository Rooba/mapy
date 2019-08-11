from io import BytesIO
from random import randint

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

    @property
    def identifier(self):
        return self._socket.getpeername()

    def close(self):
        return self._socket.close()

    async def sock_recv(self):
        return await self._loop.sock_recv(self._socket, self.recieve_size)

    async def send_packet(self, out_packet):
        packet_length = len(out_packet)
        packet = bytearray(out_packet.getvalue())

        buf = packet[:]

        final_length = packet_length + 4
        final = bytearray(final_length)
        final[0:4] = MapleAes.get_header(
            packet, self.m_siv, packet_length, VERSION)

        encrypted = shanda.encrypt_transform(buf)
        buf = MapleAes.transform(encrypted, self.m_siv)

        final[4:] = buf

        p = BytesIO()
        p.write(final)

        await self.send_packet_raw(p)

    async def send_packet_raw(self, packet):
        await self._loop.sock_sendall(self._socket, packet.getvalue())

    def manipulate_buffer(self, buffer):
        buf = bytearray(buffer)[4:]

        buf = MapleAes.transform(buf, self.m_riv)
        buf = shanda.decrypt_transform(buf)

        return buf

    @staticmethod
    def get_packet_length(headerint):
        packetlength = (headerint >> 16) ^ (headerint & 0xFFFF)
        packetlength = ((packetlength << 8) & 0xFF00)\
                        | ((packetlength >> 8) & 0xFF)
        return packetlength
