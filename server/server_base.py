import inspect

from asyncio import get_event_loop, create_task, Event
import logging
from typing import List

log = logging.getLogger(__name__)

from common.constants import HOST_IP
from net.client import ClientSocket
from net.packets.packet import PacketHandler
from net.server import Dispatcher, ClientListener
from utils.tools import wakeup

class ServerBase:
    """Server base for center, channel, and login servers
    
    Attributes
    -----------
    is_alive : bool
        Server alive status
    name: str
        Server specific name

    """
    
    def __init__(self, port, name = "", loop = None):
        self._loop = get_event_loop() if loop is None else loop

        self._ready = Event(loop=self._loop)
        self._name = name
        self._center = None
        self._is_alive = False
        self._clients = []
        self._dispatcher = Dispatcher(self)
        self._packet_handlers = []

        self.add_packet_handlers()
        self._loop.create_task(wakeup())
        
        try:
            if port:
                self._acceptor = ClientListener(self, (HOST_IP, port))
                self._ready.set()

        except Exception as e:
            self.close(e)
        
        self.is_alive = True

    def start_acceptor(self, port):
        self._acceptor = ClientListener(self, (HOST_IP, port))
        self._ready.set()

    async def on_client_accepted(self, socket):
        client = ClientSocket(socket)
        maple_client = await getattr(self, 'client_connect')(client)

        log.debug("[%s] Acepted %s", self._name, client.identifier)

        self._clients.append(maple_client)

        try:
            await maple_client.initialize()

        except IOError:
            log.debug("[%s] Client Disconnect %s", self.name, client.identifier)

            self._clients.remove(self)
        finally:
            # self._clients.remove(self)
            pass

    def add_packet_handlers(self):
        members = inspect.getmembers(self)
        for _, member in members:
            # register all packet handlers for server

            if isinstance(member, PacketHandler) and member not in self._packet_handlers:
                self._packet_handlers.append(member)

    async def wait_until_ready(self):
        """|coro|

        Waits until the GameServer has started listening for clients.
        """
        await self._ready.wait()

    def close(self, reason = "unknown"):
        print(f"{self.name} shutdown due to : {reason}")
        self.is_alive = False

    def listen(self):
        return self._acceptor._listen()

    @property
    def is_alive(self):
        return self._is_alive

    @is_alive.setter
    def is_alive(self, val: bool):
        self._is_alive = val
    
    @property
    def name(self):
        return self._name