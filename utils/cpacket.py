from net import packets
from net.packets import CSendOps


class CPacket:
    def __init__(self):
        pass

    @staticmethod
    def check_password_result(client=None, response=None):
        packet = packets.Packet(op_code=CSendOps.LP_CheckPasswordResult)

        if response != 0:
            packet.encode_int(response)
            packet.encode_short(0)
            return packet

        packet.encode_byte(0)
        packet.encode_byte(0)
        packet.encode_int(0)

        packet.encode_int(client.account.id)
        packet.encode_byte(client.account.gender)
        packet.encode_byte(0)
        packet.encode_short(0)
        packet.encode_byte(0)
        packet.encode_string(client.account.username)
        packet.encode_byte(0)
        packet.encode_byte(0)
        packet.encode_long(0)
        packet.encode_long(0)
        packet.encode_int(4)

        packet.encode_byte(True)
        packet.encode_byte(1)

        packet.encode_long(0)

        return packet

    @staticmethod
    def world_information(world):

        packet = packets.Packet(op_code=CSendOps.LP_WorldInformation)
        packet.encode_byte(world.id)
        packet.encode_string(world.name)
        packet.encode_byte(2)  # 0 : Normal 1 : Event 2 : New 3 : Hot
        packet.encode_string("Issa Event")
        packet.encode_short(100)
        packet.encode_short(100)
        packet.encode_byte(False)

        packet.encode_byte(2)

        for i in range(2):
            packet.encode_string(f"{world.name}-{i}")
            packet.encode_int(100)  # Online Count
            packet.encode_byte(1)
            packet.encode_byte(i)
            packet.encode_byte(False)

        packet.encode_short(0)

        return packet

    @staticmethod
    def end_world_information():
        packet = packets.Packet(op_code=CSendOps.LP_WorldInformation)
        packet.encode_byte(0xFF)
        return packet

    @staticmethod
    def last_connected_world(world_id):
        packet = packets.Packet(op_code=CSendOps.LP_LatestConnectedWorld)
        # default: WorldID, 253: None, 255: Recommended World
        packet.encode_int(world_id)
        return packet

    @staticmethod
    def send_recommended_world(worlds):
        packet = packets.Packet(op_code=CSendOps.LP_RecommendWorldMessage)
        packet.encode_byte(len(worlds))

        for world in worlds:
            packet.encode_int(world.id)
            packet.encode_string(world.event_message)

        return packet

    @staticmethod
    def check_user_limit(status):
        packet = packets.Packet(op_code=CSendOps.LP_CheckUserLimitResult)

        # 0: Open 1: Over user limit
        packet.encode_byte(0)
        # 0: Normal 1: Highly Populated 2: Full
        packet.encode_byte(status)
        return packet

    @staticmethod
    def world_result(characters):
        packet = packets.Packet(op_code=CSendOps.LP_SelectWorldResult)

        packet.encode_byte(0)
        packet.encode_byte(len(characters))

        for character in characters:
            CPacket.add_character_result(packet, character)

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

        packet.encode_byte(False)  # VAC
        packet.encode_byte(False)  # Ranking

    @staticmethod
    def extra_char_info(character):
        packet = packets.Packet(op_code=CSendOps.LP_CheckExtraCharInfoResult)
        return packet

    @staticmethod
    def start_view_all_characters(characters):
        packet = packets.Packet(op_code=CSendOps.LP_ViewAllCharResult)
        packet.encode_byte(1)
        packet.encode_int(2)
        packet.encode_int(len(characters))
        return packet

    @staticmethod
    def view_all_characters(world, characters):
        packet = packets.Packet(op_code=CSendOps.LP_ViewAllCharResult)

        packet.encode_byte(0)
        packet.encode_byte(world.id)

        characters = list(
            filter(
                lambda character: character.world_id == world.id,
                characters
            )
        )

        packet.encode_byte(len(characters))

        for character in characters:
            character.encode_stats(packet)
            character.encode_look(packet)

            packet.encode_byte(0)  # VAC rank?

        packet.encode_byte(2)
        return packet

    @staticmethod
    def create_new_character(character, response: bool):
        packet = packets.Packet(op_code=CSendOps.LP_CreateNewCharacterResult)
        packet.encode_byte(response)

        if not response:
            CPacket.add_character_result(packet, character)

        return packet
