from net.packets.packet import Packet
from net.packets.opcodes import CSendOps

class COutPacket:
    
    @staticmethod
    def check_password_result(client, return_response):
        packet = Packet(op_code=CSendOps.CheckPasswordResult)

        if return_response != 0:
            packet.encode_int(return_response)
            packet.encode_short(0)
            return packet
        
        packet.encode_byte(0)
        packet.encode_byte(0)
        packet.encode_int(0)
        packet.encode_int(client.account.id)
        packet.encode_byte(0)
        packet.encode_byte(0)
        packet.encode_short(0)
        packet.encode_byte(0)
        packet.encode_string(client.account.name)
        packet.encode_byte(0)
        packet.encode_byte(0)
        packet.encode_long(0)
        packet.encode_int(1)
        packet.encode_byte(1)
        packet.encode_byte(0)
        
        packet.encode_long(0)
        packet.encode_long(0)
        packet.encode_long(0)

        return packet