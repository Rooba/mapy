from net import packets
from net.packets import CSendOps

class CPacket:
    def __init__(self):
        pass

    @staticmethod
    def check_password_result(client, return_response):
        packet = packets.Packet(op_code=CSendOps.LP_CheckPasswordResult)

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
        packet.encode_string(client.account.username)
        packet.encode_byte(0)
        packet.encode_byte(0)
        packet.encode_long(0)
        packet.encode_long(0)
        packet.encode_int(1)
        packet.encode_byte(1)
        packet.encode_byte(0)
        
        packet.encode_long(0)
        packet.encode_long(0)
        packet.encode_long(0)

        return packet
    
    @staticmethod
    def world_information(world):
        packet = packets.Packet(op_code=CSendOps.LP_WorldInformation)
        packet.encode_short(15)
        packet.encode_string("Kastia")
        packet.encode_byte(0)
        packet.encode_string("Henlo Friends")
        packet.encode_short(100)
        packet.encode_short(100)
        packet.encode_byte(0)
        
        packet.encode_byte(1)

        for i in range(1):
            packet.encode_string(f"Kastia-{i}")
            packet.encode_int(200)
            packet.encode_byte(1)
            packet.encode_byte(1)
            packet.encode_byte(0)
        
        packet.encode_short(1)

        packet.encode_short(130)
        packet.encode_short(300)
        packet.encode_string("KERNEL BIG       GAY?")

        return packet

    @staticmethod
    def end_world_information():
        packet = packets.Packet(op_code=CSendOps.LP_WorldInformation)
        packet.encode_byte(0xFF)
        return packet
    
    @staticmethod
    def latest_connected_world(world):
        packet = packets.Packet(op_code=CSendOps.LP_LatestConnectedWorld)
        packet.encode_int(15)
        return packet

    @staticmethod
    def check_duplicated_id_result(name, is_available):
        packet = packets.Packet(op_code=CSendOps.LP_CheckDuplicatedIDResult)
        packet.encode_string(name)
        packet.encode_byte(is_available)
        return packet