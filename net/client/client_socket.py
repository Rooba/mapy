from random import randint
import struct

from asyncio import create_task, Lock, get_event_loop

from common.constants import VERSION, SUB_VERSION, LOCALE
from net.packets.crypto import MapleCryptograph, MapleIV, MapleAes, shanda
from net.packets.packet import Packet

class ClientSocket:
    def __init__(self, socket):
        self._loop = get_event_loop()
        self._socket = socket
        self._lock = Lock()
        self.recieve_size = 16384
        self.m_riv = None
        self.m_siv = None

        # create_task(self.listen_packets())
    
    @property
    def identifier(self):
        return self._socket.getpeername()

    async def sock_recv(self):
        return await self._loop.sock_recv(self._socket, self.recieve_size)

    async def send_packet(self, packet):
        packet_length = len(packet)
        packet = packet.getvalue()

        final_length = len(packet) + 4
        final = bytearray(final_length)

        final = MapleAes.get_header(final, self.m_siv, packet_length, VERSION)
        final[4:] = packet

        buf = final[4:][:]
        buf = shanda.encrypt_transform(buf)
        buf = MapleAes.transform(buf, self.m_siv)

        await self.send_packet_raw(buf)

    async def send_packet_raw(self, packet):
        await self._loop.sock_sendall(self._socket, packet.getvalue())

    def manipulate_buffer(self, buffer):
        
        header = struct.unpack('!i', buffer[:4])[0]
        # print(header)

        packet_length = self.get_packet_length(header)

        buf = bytearray(buffer)[4:]

        # size = MapleAes.get_length(buf)
        buf = MapleAes.transform(buf, self.m_riv)

        print(packet_length, len(buf), buf)

        buf = shanda.decrypt_transform(buf)

        return buf

    def check_header(self, header):
        header = (
                  header >> 24 & 0xFF,
                  header >> 16 & 0xFF
                  )
        first = (header[0] ^ int(self.m_riv) >> 16) & 0xFF
        second = (VERSION >> 8) & 0xFF
        third = (header[1] ^ int(self.m_riv) >> 24) & 0xFF
        fourth = VERSION & 0xFF
        return first == second and third == fourth

    def get_packet_length(self, headerint):
        packetlength = (headerint >> 16) ^ (headerint & 0xFFFF)
        packetlength = ((packetlength << 8) & 0xFF00) | ((packetlength >> 8) & 0xFF)
        return packetlength 