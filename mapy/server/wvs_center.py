import signal
from asyncio import get_event_loop
from configparser import ConfigParser
from time import time

from mapy import log
from mapy.common.constants import CHANNEL_COUNT, GAME_PORT
from mapy.common.enum import Worlds
from mapy.db import DatabaseClient
from mapy.http_api import HTTPServer
from mapy.utils import wakeup

from .world import World
from .wvs_game import WvsGame
from .wvs_login import WvsLogin


class WvsCenter:
    _name = "Server Core"

    """Server connection listener for incoming client socket connections

    Attributes
    -----------
    is_alive: :class:`bool`
        Server alive status
    name: :class:`str`
        Server specific name
    login: :class:`LoginServer`
        Registered :class:`Login` Server
    _worlds: :class:`Worlds`[:class:`World`]
        List of registered :class:`World` clients
    shop: :class:`ShopServer`
        Connected `ShopServer`

    """

    def __init__(self):
        self._loop = get_event_loop()
        self._http_api = HTTPServer(self, port=54545)
        self._clients = []
        self._pending_logins = []
        self._login = None
        self._shop = None
        self._worlds = {}
        self._load_config()

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, login):
        self._login = login

    @property
    def shop(self):
        return self._shop

    @shop.setter
    def shop(self, shop):
        self._shop = shop

    @property
    def worlds(self):
        return self._worlds

    def log(self, message, level=None):
        level = level or "info"
        getattr(log, level)(f"{self._name} {message}")

    def _load_config(self):
        self._config = ConfigParser()
        self._config.read("config.ini")
        if len(self._config.sections()) < 1:
            self._make_config()

    def _make_config(self):
        self.log("Please setup the database and other configuration")
        self._config.add_section("database")
        self._config["database"]["user"] = input("DB User: ")
        self._config["database"]["password"] = input("DB Password: ")
        self._config["database"]["host"] = input("DB Host: ")
        self._config["database"]["port"] = input("DB Port: ")
        self._config["database"]["database"] = input("DB Name: ")

        self._config.add_section("worlds")

        use_worlds = input("Setup worlds? (y/n) [Defaults will be used otherwise] ")
        if use_worlds.lower() in ["y", "yes"]:
            world_num = int(input("Number of worlds: [Max 20] "))
            for i in range(world_num):
                name = Worlds(i).name
                self.log(f"Setting up {Worlds(i).name}...")

                self._config["worlds"][name] = "active"
                self._config[name] = {}
                self._config[name]["channels"] = input("Channels: ")
                self._config[name]["exp_rate"] = input("Exp Rate: ")
                self._config[name]["drop_rate"] = input("Drop Rate: ")
                self._config[name]["meso_rate"] = input("Meso Rate: ")

        else:
            self._config["worlds"]["Scania"] = "active"
            self._config["Scania"] = {
                "channels": 3,
                "exp_rate": 1.0,
                "drop_rate": 1.0,
                "meso_rate": 1.0,
            }

        with open("config.ini", "w") as config:
            self._config.write(config)

    @classmethod
    def run(cls):
        self = WvsCenter()
        self._http_api.run()
        loop = self._loop

        try:
            loop.add_signal_handler(signal.SIGINT, loop.stop)
            loop.add_signal_handler(signal.SIGTERM, loop.stop)
        except NotImplementedError:
            pass

        def stop_loop_on_completion(f):
            loop.stop()

        future = loop.create_task(self.start())
        future.add_done_callback(stop_loop_on_completion)

        try:
            loop.run_forever()

        except KeyboardInterrupt:
            self.log(f"Received signal to terminate event loop", "warning")
            loop.run_until_complete(self.data.stop())

        finally:
            future.remove_done_callback(stop_loop_on_completion)
            loop.run_until_complete(loop.shutdown_asyncgens())
            self.log(f"Closed {self._name}", "warning")

    async def start(self):
        self._start_time = int(time())
        self.log("Initializing Server", "debug")

        self.data = DatabaseClient(loop=self._loop, **self._config["database"])
        await self.data.start()

        channel_port = GAME_PORT
        self.login = await WvsLogin.run(self)

        for world in self._config["worlds"]:
            if self._config["worlds"][world] != "active":
                continue

            world_id = Worlds[world.title()].value
            world = World(world_id)

            for channel_id in range(CHANNEL_COUNT):
                channel = await WvsGame.run(self, channel_port, world_id, channel_id)
                world.add_channel(channel)
                channel_port += 1

            self.worlds[world_id] = world
            self.login.add_world(world)

        await wakeup()

    @property
    def uptime(self):
        return int(time()) - self._start_time

    @property
    def population(self):
        return len(self._clients) + self.login.population