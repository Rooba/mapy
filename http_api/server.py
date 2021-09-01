from aiohttp import web
from os import walk
import importlib

from utils import log

class HTTPServer(web.Application):
    def __init__(self, server, loop, port=54545, route_path="http_api/routes/"):
        super().__init__(loop=loop)

        self._server = server
        self._port = port
        self._routes = []
        self._route_path = route_path

        self.load_routes()

    def load_routes(self):
        for path, _, files in walk(self._route_path):
            for file_ in files:
                if file_.endswith('.py'):
                    lib = importlib.import_module(path.replace('/', '.') + file_.replace('.py', ''))
                    if not getattr(lib, 'setup'):
                        log.warn(f"{file_} does not contain a setup method")
                        continue

                    self._routes += lib.setup(self)

        self.router.add_routes(self._routes)

    def run(self):
        runner = web.AppRunner(self)
        self.loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, port=self._port)
        self.loop.run_until_complete(site.start())

    @property
    def server(self):
        return self._server
