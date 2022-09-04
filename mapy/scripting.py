from asyncio import Queue, get_running_loop
from dataclasses import dataclass
from io import TextIOBase
from pathlib import Path

from aiofiles import open as async_open

from .opcodes import CSendOps
from .packet import Packet


class ScriptBase:
    __script_cache__ = {}

    def __init__(self, script, client):
        self._file_contents = TextIOBase()
        self._script = None
        self._parent = client
        self._context = None
        self._read_task = get_running_loop().create_task(self.read_file(script))

    async def read_file(self, path):
        try:
            if self.__script_cache__.get(path.name, None):
                self._file_contents = self.__script_cache__[path.name]
            else:
                async with async_open(path, "r") as f:
                    self._file_contents.write(await f.read())
                    self._file_contents.seek(0)
                    self.__script_cache__[path.name] = self._file_contents

            self._script = compile(
                "async def ex():\n"
                + "".join([f"    {line}" for line in self._file_contents.readlines()]),
                "<string>",
                "exec",
            )
            self._file_contents.seek(0)

        finally:
            return True

    async def execute(self):
        async def run(script, _globals):
            exec(script, _globals)
            await _globals["ex"]()

        env = {"ctx": self._context}
        env.update(globals())
        await run(self._script, env)

        self._parent.npc_script = None

    @property
    def parent(self):
        return self._parent


class NpcScript(ScriptBase):
    def __init__(self, client, /, npc_id=None, default=False, file=None):
        script = Path()
        if not file:
            script = Path(
                f"scripts/npc/{'default' if default or not npc_id else npc_id}.py"
            )
        else:
            if isinstance(file, Path):
                script = file

        if not script.exists():
            return

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
        if (p := Path(f"scripts/npc/{npc_id}.py")).exists() and p.is_file():
            return NpcScript(client, file=p)
        return NpcScript(client, default=True)


class ContextBase:
    def __init__(self, script):
        self._script = script


@dataclass
class Message:
    msg: str = ""
    prev: bool = False
    nxt: bool = False

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
