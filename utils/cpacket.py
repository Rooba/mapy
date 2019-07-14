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
        packet.encode_byte(world.id)
        packet.encode_string(world.name)
        packet.encode_byte(0)
        packet.encode_string("Henlo Friends")
        packet.encode_short(100)
        packet.encode_short(100)
        packet.encode_byte(0)
        
        packet.encode_byte(2)

        for i in range(2):
            packet.encode_string("%s-%s" % (world.name, i))
            packet.encode_int(200)
            packet.encode_byte(world.id)
            packet.encode_byte(i)
            packet.encode_byte(0)
        
        packet.encode_short(0)

        # packet.encode_short()
        # packet.encode_short()
        # packet.encode_string()

        return packet

    @staticmethod
    def end_world_information():
        packet = packets.Packet(op_code=CSendOps.LP_WorldInformation)
        packet.encode_byte(0xFF)
        return packet
    
    @staticmethod
    def latest_connected_world(world):
        packet = packets.Packet(op_code=CSendOps.LP_LatestConnectedWorld)
        packet.encode_int(world.id)
        return packet

    @staticmethod
    def check_user_limit(status):
        packet = packets.Packet(op_code=CSendOps.LP_CheckUserLimitResult)
        packet.encode_byte(0)       # 1 if past user limit
        packet.encode_byte(status) # 0 - Normal, 1 - Highly Populated, 2 - Full
        return packet

    @staticmethod
    def world_result(characters):
        packet = packets.Packet(op_code=CSendOps.LP_SelectWorldResult)

        packet.encode_byte(0)
        packet.encode_byte(len(characters))

        for character in characters:
            CPacket.add_character_result(packet, character)
        
        print("After")
        print(packet.to_string())
        packet.encode_byte(2)
        packet.encode_int(3)
        packet.encode_int(0)

        return packet

    @staticmethod
    def check_duplicated_id_result(name, is_available):
        packet = packets.Packet(op_code=CSendOps.LP_CheckDuplicatedIDResult)
        packet.encode_string(name)
        packet.encode_byte(is_available)
        return packet

    @staticmethod
    def add_character_result(packet, character):
        character.encode_stats(packet)
        character.encode_look(packet)

        packet.encode_byte(0)\
        .encode_byte(False)

