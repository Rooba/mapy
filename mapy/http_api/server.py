from aiohttp import web
from os import walk
import importlib

from mapy import log


class HTTPServer(web.Application):
    def __init__(self, server_core, port=None, loop=None):
        self._name = "HTTP API"
        self._server = server_core
        self._loop = server_core._loop
        self._port = port
        self._routes = None

        super().__init__(loop=self._loop)
        self.load_routes()

    def load_routes(self):
        self._routes = importlib.import_module(".routes", "mapy.http_api")
        self.router.add_routes(self._routes.Routes(self))

    def run(self):
        runner = web.AppRunner(self)
        self.loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, port=self._port)
        self.loop.run_until_complete(site.start())
        self.log(f"Listening on port <lr>{self._port}</lr>", "info")

    @property
    def server(self):
        return self._server

    def log(self, message, level=None):
        level = level if level else "debug"
        getattr(log, level)(f"{self._name} {message}")
