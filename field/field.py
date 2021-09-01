from .foothold_manager import FootholdManager
from .portal_manager import PortalManager
from .mob_pool import MobPool
from .npc_pool import NpcPool
from .user_pool import UserPool

from utils import CPacket, get

class Field:
    def __init__(self, map_id):
        self.map_id = map_id
        # self.characters = []
        # self.sockets = {}

        self.portals = PortalManager()
        self.footholds = FootholdManager()
        self.clients = UserPool(self)
        self.mobs = MobPool(map_id)
        self.npcs = NpcPool(map_id)

    @property
    def id(self):
        return self.map_id

    async def add(self, client):
        character = client.character

        if client.sent_char_data:
            await client.send_packet(CPacket.set_field(character, False, client.channel_id))

        else:
            client.sent_char_data = True
            character.stats.portal = 0

            await client.send_packet(CPacket.set_field(character, True, client.channel_id))
        
        for _character in self.clients.characters:
            await client.send_packet(CPacket.user_enter_field(_character))
        
        await self.spawn_mobs(client)
        await self.spawn_npcs(client)

        self.clients.add(client)

        await self.broadcast(CPacket.user_enter_field(character))
        
    async def broadcast(self, packet, *ignore):
        for client in self.clients:
            if client in ignore or client.character in ignore:
                continue
        
            await client.send_packet(packet)

    async def swap_mob_controller(self, client, mob):
        if mob.controller:
            controller = next(filter(lambda c: c.character.id == mob.controller), None)
            if controller:
                await controller.send_packet(CPacket.mob_change_controller(mob, 0))
        
        mob.controller = client.character.id
        await client.send_packet(CPacket.mob_change_controller(mob, 1))

    async def spawn_mobs(self, client):
        for mob in self.mobs:
            if mob.controller == 0:
                await self.swap_mob_controller(client, mob)
            
            await client.send_packet(CPacket.mob_enter_field(mob))

    async def spawn_npcs(self, client):
        for npc in self.npcs:
            await client.send_packet(CPacket.npc_enter_field(npc))

