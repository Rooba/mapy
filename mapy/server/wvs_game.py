from ..client.wvs_game_client import WvsGameClient
from ..common.enum import Worlds
from ..common.constants import ANTIREPEAT_BUFFS, is_event_vehicle_skill
from ..net.opcodes import CRecvOps
from ..net.packet import packet_handler
from ..scripts.npc.npc_script import NpcScript
from ..cpacket import CPacket

from .wvs_login import PendingLogin
from .server_base import ServerBase


class WvsGame(ServerBase):
    def __init__(self, parent, port, world_id, channel_id):
        super().__init__(parent, port)
        self._name = f"Game Server[{world_id}][{channel_id}]"
        self._field_manager = {}
        self._allow_multi_leveling = False

        self.world_id = world_id
        self.world_name = Worlds(world_id).name
        self.channel_id = channel_id
        self.ticker_message = "In game wow"
        self.meso_rate = int(parent._config[self.world_name]["meso_rate"])
        self.drop_rate = int(parent._config[self.world_name]["drop_rate"])
        self.exp_rate = int(parent._config[self.world_name]["exp_rate"])
        self.quest_exp_rate = 1
        self.party_quest_exp_rate = 1

    @classmethod
    async def run(cls, *args):
        game = WvsGame(*args)
        await game.start()
        return game

    async def client_connect(self, client):
        game_client = WvsGameClient(self, client)
        self._parent._clients.append(game_client)
        return game_client

    async def on_client_disconnect(self, client):
        field = await client.get_field()
        field.clients.remove(client)
        # field.sockets.pop(client.character)
        await field.broadcast(CPacket.user_leave_field(client.character))

        self._parent._clients.remove(client)
        await super().on_client_disconnect(client)

    async def get_field(self, field_id):
        field = self._field_manager.get(field_id, None)
        if field:
            return field

        field = await self.data.field.get(field_id)
        self._field_manager[field_id] = field

        return field

    @packet_handler(CRecvOps.CP_MigrateIn)
    async def handle_migrate_in(self, client, packet):
        uid = packet.decode_int()
        packet.decode_buffer(16)  # Machine ID
        packet.decode_byte()  # is gm
        packet.decode_byte()
        packet.decode_long()  # Session ID

        login_req: PendingLogin | None

        for x in self.parent._pending_logins:
            if x.character.id == uid:
                login_req = x
                break

        else:
            login_req = None

        if not login_req:
            return await client.disconnect()

        login_req.migrated = True
        login_req.character._client = client

        client.character = await self.data.characters.load(uid, client)
        await (await self.get_field(client.character.field_id)).add(client)

        await client.send_packet(CPacket.claim_svr_changed(True))
        await client.send_packet(CPacket.set_gender(client.character.stats.gender))
        await client.send_packet(CPacket.func_keys_init(client.character.func_keys))
        await client.send_packet(CPacket.broadcast_server_msg(self.ticker_message))

    @packet_handler(CRecvOps.CP_UserMove)
    async def handle_user_move(self, client, packet):
        packet.decode_long()  # v1
        packet.decode_byte()  # portal count
        packet.decode_long()  # v2
        packet.decode_int()  # map crc
        packet.decode_int()  # key
        packet.decode_int()  # key crc

        move_path = packet.decode_buffer(-1)
        client.character.position.decode_move_path(move_path)
        await client.broadcast(CPacket.user_movement(client.character.id, move_path))

    @packet_handler(CRecvOps.CP_UserSkillUseRequest)
    async def handle_skill_use_request(self, client, packet):
        packet.decode_int()  # tick count
        skill_id = packet.decode_int()
        _ = packet.decode_byte()

        if skill_id in ANTIREPEAT_BUFFS:
            packet.decode_short()  # x
            packet.decode_short()  # y

        if skill_id == 4131006:
            packet.decode_int()

        if is_event_vehicle_skill(skill_id):
            packet.skip(1)
            if skill_id == 2311001:
                packet.skip(2)

        packet.decode_short()

        casted = False
        if skill_id:
            casted = await client.character.skills.cast(skill_id)

        await client.send_packet(CPacket.enable_actions())

        if casted:
            client.broadcast(
                CPacket.effect_remote(
                    client.character.obj_id,
                    1,
                    skill_id,
                    client.character.stats.level,
                    1,
                )
            )

    @packet_handler(CRecvOps.CP_UserSelectNpc)
    async def handle_user_select_npc(self, client, packet):
        obj_id = packet.decode_int()
        packet.decode_short()  # x
        packet.decode_short()  # y

        if client.npc_script:
            ...  # client has npc script already?

        npc = client.character.field.npcs.get(obj_id)

        if npc:
            client.npc_script = NpcScript.get_script(npc.id, client)
            await client.npc_script.execute()

    @packet_handler(CRecvOps.CP_UserScriptMessageAnswer)
    async def handle_user_script_message_answer(self, client, packet):
        script = client.npc_script

        type_ = packet.decode_byte()
        type_expected = script.last_msg_type

        if type_ != type_expected:
            self.log(
                f"User answered type: [{type_}], expected [{type_expected}]" "debug"
            )
            return

        resp = packet.decode_byte()
        self.log(f"Script response: [{resp}]")

        if type_ == 0:
            if resp == 255:
                script.end_chat()
            elif resp == 0:
                await script.proceed_back()
            elif resp == 1:
                await script.proceed_next(resp)

    @packet_handler(CRecvOps.CP_UpdateGMBoard)
    async def handle_update_gm_board(self, client, packets):
        ...

    @packet_handler(CRecvOps.CP_RequireFieldObstacleStatus)
    async def handle_require_field_obstacle(self, client, packets):
        ...
