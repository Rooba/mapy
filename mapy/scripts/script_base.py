class ScriptBase:

    def __init__(self, script, client):
        self._parent = client
        self._script = compile(
            "async def ex():\n" +
            "".join([ f"    {line}" for line in open(script, "r").readlines() ]),
            "<string>",
            "exec",
        )
        self._context = None

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