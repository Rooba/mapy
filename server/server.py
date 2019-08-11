import signal

from asyncio import get_event_loop, create_task, Event, Task
# from loguru import logger

from . import World, WvsGame, WvsLogin, WvsShop
from web import HTTPClient
from utils.tools import wakeup
from net.packets.opcodes import InterOps
from net.packets.packet import packet_handler, Packet
from utils import log, logger
from client import WvsCenterClient
from common.constants import (HOST_IP, GAME_PORT, USE_DATABASE,
    USE_HTTP_API, WORLD_COUNT, CHANNEL_COUNT)


class ServerApp:
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
        self.name = "ServerApp"
        self._loop = get_event_loop()
        self._clients = []

        self.login = None
        self._shop = None
        self._worlds = []

    @classmethod
    def run(cls):
        self = ServerApp()

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
            log.warning(f"{self.name} Received signal to terminate event loop")

        finally:
            future.remove_done_callback(stop_loop_on_completion)
            loop.run_until_complete(loop.shutdown_asyncgens())
            log.warning(f"{self.name} Closed {self.name}")

    async def start(self):
        log.info("Initializing Server")

        if USE_HTTP_API:
            log.info("Setup HTTP Client")
            self.data = HTTPClient(loop=self._loop)

        channel_port = GAME_PORT

        self.login = await WvsLogin.run(self)

        for world_id in range(WORLD_COUNT):
            world = World(world_id)

            for channel_id in range(CHANNEL_COUNT):
                channel = await WvsGame.run(self, channel_port, world_id, channel_id)
                world.add_channel(channel)
                channel_port += 1

            self._worlds.append(world)
            self.login.add_world(world)

        await wakeup()

