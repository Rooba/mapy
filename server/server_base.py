import inspect

from asyncio import get_event_loop, create_task, Event
import logging

log = logging.getLogger(__name__)

from common.constants import HOST_IP
from net.client import ClientSocket
from net.packets.packet import PacketHandler
from net.server import Dispatcher, ClientListener
from utils.tools import wakeup
from web import HTTPClient

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
        self._packet_handlers = []
        self._dispatcher = Dispatcher(self)
        self._api = HTTPClient(loop=self._loop)
        self.add_packet_handlers()
        self._loop.create_task(wakeup())
        
        if port:
            self._acceptor = ClientListener(self, (HOST_IP, port))
            self._ready.set()

        self.is_alive = True

    def start_acceptor(self, port):
        self._acceptor = ClientListener(self, (HOST_IP, port))
        self._ready.set()

    async def on_client_accepted(self, socket):
        client = ClientSocket(socket)
        maple_client = await getattr(self, 'client_connect')(client)

        log.debug("[%s] Acepted %s", self._name, client.identifier)

        self._clients.append(maple_client)
        await maple_client.initialize()

    async def on_client_disconnect(self, client):
        self._clients.remove(client)
        client._receive_task.cancel()

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

    def listen(self):
        return self._acceptor._listen()

    @property
    def dispatcher(self):
        return self._dispatcher

    @property
    def is_alive(self):
        return self._is_alive

    @is_alive.setter
    def is_alive(self, val: bool):
        self._is_alive = val
    
    @property
    def name(self):
        return self._name