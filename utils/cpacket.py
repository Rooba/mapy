from net import packets
from net.packets import CSendOps

class CPacket:
    def __init__(self):
        pass

    @staticmethod
    def check_password_result(client, return_response):
        packet = packets.Packet(op_code=CSendOps.CheckPasswordResult)

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
    
    @staticmethod
    def check_duplicated_id_result(name, is_available):
        packet = packets.Packet(op_code=CSendOps.LP_CheckDuplicatedIDResult)
        packet.encode_string(name)
        packet.encode_byte(is_available)
        return packet