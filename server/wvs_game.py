from common.enum import Worlds
from net.packets.opcodes import CRecvOps
from net.packets import crypto, Packet
from net.packets.packet import packet_handler
from .server_base import ServerBase

class WvsGame(ServerBase):
    def __init__(self, parent, port, world_id, channel_id):
        super().__init__(parent, port, f'GameServer({world_id})({channel_id})')

        self.world_id = world_id
        self.world_name = Worlds(world_id).name
        self.channel_id = channel_id

        # Fill this in with 
        self.ticker_message = ""
        self.allow_multi_leveling = False
        self.exp_rate = 1
        self.quest_exp_rate = 1
        self.party_quest_exp_rate = 1
        self.meso_rate = 1
        self.drop_rate = 1

    @classmethod
    async def run(cls, parent, port, world_id, channel_id):
        login = WvsGame(parent, port, world_id, channel_id)

        await login.start()

        return login