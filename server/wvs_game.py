from client import WvsGameClient
from common.enum import Worlds
from net.packets.opcodes import CRecvOps
from net.packets import crypto, Packet
from net.packets.packet import packet_handler
from .server_base import ServerBase
from scripts.npc import NpcScript
from utils import CPacket, log

class WvsGame(ServerBase):
    def __init__(self, parent, port, world_id, channel_id):
        super().__init__(parent, port, f'GameServer({world_id})({channel_id})')

        self.world_id = world_id
        self.world_name = Worlds(world_id).name
        self.channel_id = channel_id
        self.field_manager = {}

        self.ticker_message = "In game wow"
        self.allow_multi_leveling = False
        self.exp_rate = int(parent._config[self.world_name]['exp_rate'])
        self.quest_exp_rate = 1
        self.party_quest_exp_rate = 1
        self.meso_rate = int(parent._config[self.world_name]['meso_rate'])
        self.drop_rate = int(parent._config[self.world_name]['drop_rate'])

    @classmethod
    async def run(cls, parent, port, world_id, channel_id):
        login = WvsGame(parent, port, world_id, channel_id)

        await login.start()

        return login

    async def client_connect(self, client):
        game_client = WvsGameClient(self, client)
        self._parent._clients.append(game_client)

        return game_client
    
    def on_client_disconnect(self, client):
        self._parent._clients.remove(client)
        super().on_client_disconnect(client)

    async def get_field(self, field_id):
        field = self.field_manager.get(field_id, None)

        if field:
            return field
        
        field = await self.data.field.get(field_id)
        self.field_manager[field_id] = field

        return field

    @packet_handler(CRecvOps.CP_MigrateIn)
    async def handle_migrate_in(self, client, packet):
        character_id = packet.decode_int()
        machine_id = packet.decode_buffer(16)
        is_gm = packet.decode_byte()
        packet.decode_byte()
        session_id = packet.decode_long()

        for x in self.parent.logged_in:
            if x.character.id == character_id:
                req = x
                break
        
        else:
            req = None

        if not req:
            await client.disconnect()
        
        req.migrated = True

        client.character = req.character
        field = await self.get_field(client.character.field_id)

        await field.add(client)
        await client.send_packet(CPacket.claim_svr_changed(True))
        await client.send_packet(CPacket.set_gender(client.character.stats.gender))
        await client.send_packet(CPacket.func_keys_init(client.character.func_keys))
        await client.send_packet(CPacket.broadcast_server_msg(self.ticker_message))

    @packet_handler(CRecvOps.CP_UserMove)
    async def handle_user_move(self, client, packet):
        v1 = packet.decode_long()
        portal_count = packet.decode_byte()
        v2 = packet.decode_long()
        map_crc = packet.decode_int()
        key = packet.decode_int()
        key_crc = packet.decode_int()

        move_path = packet.decode_buffer(-1)
        client.character.position.decode_move_path(move_path)    
        field = await client.get_field()
        await field.broadcast(CPacket.user_movement(client.character.id, move_path), client)
    
    @packet_handler(CRecvOps.CP_UserSelectNpc)
    async def handle_user_select_npc(self, client, packet):
        obj_id = packet.decode_int()
        x = packet.decode_short()
        y = packet.decode_short()

        if client.npc_script:
            pass # client has npc script already?
        
        field = await client.get_field()
        npc = field.npcs.get(obj_id)

        if npc:
            client.npc_script = NpcScript.get_script(npc.id, client)
            await client.npc_script.execute()

    @packet_handler(CRecvOps.CP_UserScriptMessageAnswer)
    async def handle_user_script_message_answer(self, client, packet):
        script = client.npc_script

        type_ = packet.decode_byte()
        type_expected = script.last_msg_type

        if type_ != type_expected:
            log.debug(f"User answered type: [{type_}], expected [{type_expected}]")
            return
        
        resp = packet.decode_byte()
        log.info(f"Script response: [{resp}]")

        if type_ == 0:
            if resp == 255:
                script.end_chat()
            elif resp == 0:
                await script.proceed_back()
            elif resp == 1:
                await script.proceed_next(resp)

    @packet_handler(CRecvOps.CP_UpdateGMBoard)
    async def handle_update_gm_board(self, client, packets):
        pass
    
    @packet_handler(CRecvOps.CP_RequireFieldObstacleStatus)
    async def handle_require_field_obstacle(self, client, packets):
        pass

