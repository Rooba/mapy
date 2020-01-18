from utils import CPacket

import scripts.npc as npc

class NpcScript:
    def __init__(self, npc_id, client):
        self._npc_id = npc_id
        self._client = client
    
    async def send_ok(self, msg):
        await self._client.send_packet(CPacket.npc_script_message(
            self._npc_id,
            0,
            msg,
            [0, 0],
            0,
            0
        ))
    
    @staticmethod
    def get_script(npc_id, client):
        return npc.DefaultScript(npc_id, client)
