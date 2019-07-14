from asyncio import get_event_loop, create_task, Event, ensure_future, Task, wait_for
import inspect
import logging
import signal

log = logging.getLogger(__name__)

from common.constants import HOST_IP, CENTER_PORT
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
    
    def __init__(self, name = ""):
        self._loop = get_event_loop()

        self._ready = Event(loop=self._loop)
        self._name = name
        self._center = None
        self._is_alive = False
        self._clients = []
        self._packet_handlers = []
        self._dispatcher = Dispatcher(self)
        self.add_packet_handlers()

    def run(self, port=None, listen=False):
        loop = self._loop

        try:
            loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
            loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
        except NotImplementedError:
            pass

        async def runner():
            try:
                await self.start(port, listen)
            finally:
                pass

        def stop_loop_on_completion(f):
            loop.stop()

        future = loop.create_task(self.start(port, listen))
        future.add_done_callback(stop_loop_on_completion)

        try:
            loop.run_forever()

        except KeyboardInterrupt:
            log.info('Received signal to terminate event loop.')

        finally:
            future.remove_done_callback(stop_loop_on_completion)
            loop.run_until_complete(loop.shutdown_asyncgens())
            log.info('[%s] Closed' % self.name)


    async def start(self, port, listen):
        self.data = HTTPClient(loop=self._loop)
        self.is_alive = True

        if self._center:
            self._center = self._center(self, HOST_IP, CENTER_PORT)
            self._loop.create_task(self._center.create_connection())

        if port:
            self._acceptor = ClientListener(self, (HOST_IP, port))

        if listen:
            self._ready.set()
            self._loop.create_task(self.listen())
        
        await wakeup()

    def close(self):
        for task in Task.all_tasks():
            task.cancel()

    def start_acceptor(self, port):
        self._acceptor = ClientListener(self, (HOST_IP, port))
        self._ready.set()

    async def on_client_accepted(self, socket):
        client = ClientSocket(socket)
        maple_client = await getattr(self, 'client_connect')(client)

        log.info("[%s] Acepted %s", self._name, client.identifier)

        self._clients.append(maple_client)
        await maple_client.initialize()

    async def on_client_disconnect(self, client):
        self._clients.remove(client)
        
        log.info("[%s] Client Disconnect", self._name)

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