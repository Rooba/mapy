from mapy import constants
from mapy.net import Packet, CSendOps


class CPacket:
    @staticmethod
    def check_password_result(client=None, response=None):
        packet = Packet(op_code=CSendOps.LP_CheckPasswordResult)

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

        packet = Packet(op_code=CSendOps.LP_WorldInformation)
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
        packet = Packet(op_code=CSendOps.LP_WorldInformation)
        packet.encode_byte(0xFF)
        return packet

    @staticmethod
    def last_connected_world(world_id):
        packet = Packet(op_code=CSendOps.LP_LatestConnectedWorld)
        # default: WorldID, 253: None, 255: Recommended World
        packet.encode_int(world_id)
        return packet

    @staticmethod
    def send_recommended_world(worlds):
        packet = Packet(op_code=CSendOps.LP_RecommendWorldMessage)
        packet.encode_byte(len(worlds))

        for world in worlds:
            packet.encode_int(world.id)
            packet.encode_string(world.event_message)

        return packet

    @staticmethod
    def check_user_limit(status):
        packet = Packet(op_code=CSendOps.LP_CheckUserLimitResult)

        # 0: Open 1: Over user limit
        packet.encode_byte(0)
        # 0: Normal 1: Highly Populated 2: Full
        packet.encode_byte(status)
        return packet

    @staticmethod
    def world_result(entries):
        packet = Packet(op_code=CSendOps.LP_SelectWorldResult)

        packet.encode_byte(0)
        packet.encode_byte(len(entries))

        for entry in entries:
            entry.encode(packet)

        packet.encode_byte(2)
        packet.encode_int(3)
        packet.encode_int(0)

        return packet

    @staticmethod
    def check_duplicated_id_result(name, is_available):
        packet = Packet(op_code=CSendOps.LP_CheckDuplicatedIDResult)
        packet.encode_string(name)
        packet.encode_byte(is_available)
        return packet

    @staticmethod
    def extra_char_info(character):
        packet = Packet(op_code=CSendOps.LP_CheckExtraCharInfoResult)
        return packet

    @staticmethod
    def start_view_all_characters(characters):
        packet = Packet(op_code=CSendOps.LP_ViewAllCharResult)
        packet.encode_byte(1)
        packet.encode_int(2)
        packet.encode_int(len(characters))
        return packet

    @staticmethod
    def view_all_characters(world, characters):
        packet = Packet(op_code=CSendOps.LP_ViewAllCharResult)

        packet.encode_byte(0)
        packet.encode_byte(world.id)

        characters = list(
            filter(lambda character: character.world_id == world.id, characters)
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
        packet = Packet(op_code=CSendOps.LP_CreateNewCharacterResult)
        packet.encode_byte(response)

        if not response:
            character.encode_entry(packet)

        return packet

    @staticmethod
    def select_character_result(uid, port):
        packet = Packet(op_code=CSendOps.LP_SelectCharacterResult)

        packet.encode_byte(0)  # world
        packet.encode_byte(0)  # selected char

        packet.encode_buffer(constants.SERVER_ADDRESS)
        packet.encode_short(port)
        packet.encode_int(uid)
        packet.encode_byte(0)
        packet.encode_int(0)

        return packet

    # ---------------- Login Server End --------------- #

    @staticmethod
    def set_field(character, character_data, channel: int):
        packet = Packet(op_code=CSendOps.LP_SetField)
        # CPacket.cclient_opt_man__encode_opt(packet, 0)
        packet.encode_short(0)

        packet.encode_int(channel)
        packet.encode_int(0)

        packet.encode_byte(1)
        packet.encode_byte(character_data)
        packet.encode_short(0)

        if character_data:
            # character.random.encode(packet)
            packet.encode_int(0)
            packet.encode_int(0)
            packet.encode_int(0)
            character.encode(packet)

            packet.encode_int(0)
            packet.encode_int(0)
            packet.encode_int(0)
            packet.encode_int(0)

        else:
            packet.encode_byte(0)
            packet.encode_int(character.field_id)
            packet.encode_byte(character.stats.portal)
            packet.encode_int(character.stats.hp)
            packet.encode_byte(0)

        packet.encode_long(150842304000000000)

        return packet

    @staticmethod
    def func_keys_init(keys):
        packet = Packet(op_code=CSendOps.LP_FuncKeyMappedInit)
        packet.encode_byte(0)

        for i in range(90):
            key = keys[i]
            packet.encode_byte(getattr(key, "type", 0))
            packet.encode_int(getattr(key, "action", 0))

        return packet

    @staticmethod
    def set_gender(gender):
        packet = Packet(op_code=CSendOps.LP_SetGender)
        packet.encode_byte(gender)
        return packet

    @staticmethod
    def stat_changed(modifier=None, excl_req=False):
        packet = Packet(op_code=CSendOps.LP_StatChanged)
        packet.encode_byte(excl_req)
        if modifier:
            modifier.encode(packet)
        else:
            packet.encode_int(4)
        packet.encode_byte(0)
        packet.encode_byte(0)

        return packet

    @staticmethod
    def enable_actions():
        return CPacket.stat_changed(excl_req=True)

    @staticmethod
    def claim_svr_changed(claim_svr_con: bool):
        packet = Packet(op_code=CSendOps.LP_ClaimSvrStatusChanged)
        packet.encode_byte(claim_svr_con)
        return packet

    # ------------------- User Pool ------------------- #

    @staticmethod
    def user_enter_field(character):
        packet = Packet(op_code=CSendOps.LP_UserEnterField)
        packet.encode_int(character.id)

        packet.encode_byte(character.stats.level)
        packet.encode_string(character.stats.name)

        packet.skip(8)

        packet.encode_long(0).encode_long(0).encode_byte(0).encode_byte(0)

        packet.encode_short(character.stats.job)
        character.encode_look(packet)

        packet.encode_int(0)  # driver ID
        packet.encode_int(0)  # passenger ID
        packet.encode_int(0)  # choco count
        packet.encode_int(0)  # active effeect item ID
        packet.encode_int(0)  # completed set item ID
        packet.encode_int(0)  # portable chair ID

        packet.encode_short(0)  # private?

        packet.encode_short(0)
        packet.encode_byte(character.position.stance)
        packet.encode_short(character.position.foothold)
        packet.encode_byte(0)  # show admin effect

        packet.encode_byte(0)  # pets?

        packet.encode_int(0)  # taming mob level
        packet.encode_int(0)  # taming mob exp
        packet.encode_int(0)  # taming mob fatigue

        packet.encode_byte(0)  # mini room type

        packet.encode_byte(0)  # ad board remote
        packet.encode_byte(0)  # on couple record add
        packet.encode_byte(0)  # on friend record add
        packet.encode_byte(0)  # on marriage record add

        packet.encode_byte(0)  # some sort of effect bit flag

        packet.encode_byte(0)  # new year card record add
        packet.encode_int(0)  # phase
        return packet

    @staticmethod
    def user_leave_field(character):
        packet = Packet(op_code=CSendOps.LP_UserLeaveField)
        packet.encode_int(character.id)
        return packet

    @staticmethod
    def user_movement(uid, move_path):
        packet = Packet(op_code=CSendOps.LP_UserMove)
        packet.encode_int(uid)
        packet.encode_buffer(move_path)
        return packet

    # --------------------- Mob Pool ------------------- #

    @staticmethod
    def mob_enter_field(mob):
        packet = Packet(op_code=CSendOps.LP_MobEnterField)
        mob.encode_init(packet)
        return packet

    @staticmethod
    def mob_change_controller(mob, level):
        packet = Packet(op_code=CSendOps.LP_MobChangeController)
        packet.encode_byte(level)

        if level == 0:
            packet.encode_int(mob.obj_id)
        else:
            mob.encode_init(packet)

        return packet

    # --------------------- Npc Pool ----------------------#

    @staticmethod
    def npc_enter_field(npc):
        packet = Packet(op_code=CSendOps.LP_NpcEnterField)
        packet.encode_int(npc.obj_id)
        packet.encode_int(npc.life_id)

        packet.encode_short(npc.x)
        packet.encode_short(abs(npc.cy))
        packet.encode_byte(npc.f != 1)
        packet.encode_short(npc.foothold)

        packet.encode_short(npc.rx0)
        packet.encode_short(npc.rx1)

        packet.encode_byte(True)

        return packet

    @staticmethod
    def npc_script_message(npc, msg_type, msg, end_bytes, type_, other_npc):
        packet = Packet(op_code=CSendOps.LP_ScriptMessage)

        packet.encode_byte(4)
        packet.encode_int(npc)
        packet.encode_byte(msg_type)
        packet.encode_byte(type_)

        if type_ in [4, 5]:
            packet.encode_int(other_npc)

        packet.encode_string(msg)

        if end_bytes:
            packet.encode(bytes(end_bytes))

        return packet

    @staticmethod
    def broadcast_server_msg(msg):
        return CPacket.broadcast_msg(4, msg)

    @staticmethod
    def broadcast_msg(type_, msg):
        packet = Packet(op_code=CSendOps.LP_BroadcastMsg)
        packet.encode_byte(type_)

        if type_ == 4:
            packet.encode_byte(True)

        packet.encode_string(msg)
        return packet
