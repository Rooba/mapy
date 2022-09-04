from asyncio import Queue
from os.path import isfile

from mapy.opcodes import CSendOps
from mapy.packet import Packet
from mapy.scripts.script_base import ScriptBase
from mapy.scripts.npc.npc_context import NpcContext


class NpcScript(ScriptBase):
    def __init__(self, npc_id, client, default=False):
        if default:
            script = f"scripts/npc/default.py"
        else:
            script = f"scripts/npc/{npc_id}.py"

        super().__init__(script, client)
        self._npc_id = npc_id
        self._context = NpcContext(self)
        self._last_msg_type = None

        self._prev_msgs = []
        self._prev_id = 0
        self._response = Queue(maxsize=1)

    @property
    def npc_id(self):
        return self._npc_id

    @property
    def last_msg_type(self):
        return self._last_msg_type

    async def send_message(self, type_, action, flag=4, param=0):
        await self.send_dialogue(type_, action, flag, param)

        resp = await self._response.get()
        return resp

    async def send_dialogue(self, type_, action, flag, param):
        packet = Packet(op_code=CSendOps.LP_ScriptMessage)
        packet.encode_byte(flag)
        packet.encode_int(self._npc_id)
        packet.encode_byte(type_)
        packet.encode_byte(param)

        action(packet)

        self._last_msg_type = type_
        self._response.task_done()
        await self._parent.send_packet(packet)

    async def reuse_dialogue(self, msg):
        await self.send_dialogue(0, msg.encode, 4, 0)

    async def proceed_back(self):
        if self._prev_id == 0:
            return

        self._prev_id -= 1

        await self.reuse_dialogue(self._prev_msgs[self._prev_id])

    async def proceed_next(self, resp):
        self._prev_id += 1

        if self._prev_id < len(self._prev_msgs):
            await self.reuse_dialogue(self._prev_msgs[self._prev_id])

        else:
            self._response.task_done()
            await self._response.put(resp)

    def end_chat(self):
        self.parent.npc_script = None
        self._response.task_done()

    @staticmethod
    def get_script(npc_id, client):
        if isfile(f"scripts/npc/{npc_id}.py"):
            return NpcScript(npc_id, client)
        return NpcScript(npc_id, client, default=True)
