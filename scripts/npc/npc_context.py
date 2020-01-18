from dataclasses import dataclass
from scripts.context_base import ContextBase

@dataclass
class Message:
    msg: str    = ""
    prev: bool  = False
    nxt: bool   = False

    def encode(self, packet):
        packet.encode_string(self.msg)
        packet.encode_byte(self.prev)
        packet.encode_byte(self.nxt)

class NpcContext(ContextBase):
    @property
    def npc_id(self):
        return self._script.npc_id
    
    async def say(self, msg, prev=False, nxt=False):
        self._script._prev_msgs.append(Message(msg, prev, nxt))
        
        def action(packet):
            packet.encode_string(msg)
            packet.encode_byte(prev)
            packet.encode_byte(nxt)

        await self._script.send_message(0, action)
    
    async def ask_yes_no(self, msg):
        def action(packet):
            packet.encode_string(msg)
        
        await self._script.send_message(2, action)
    
    def end_chat(self):
        self._script.end_chat()
