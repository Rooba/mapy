import scripts.npc.npc_script as npc_script

class DefaultScript(npc_script.NpcScript):
    async def execute(self):
        await self.send_ok("I am the default script")