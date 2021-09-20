from asyncio import Event, get_event_loop, get_running_loop, run_coroutine_threadsafe
from socket import AF_INET, IPPROTO_TCP, SOCK_STREAM, TCP_NODELAY, socket

from net.client import ClientSocket
from net.packets.packet import PacketHandler
from net.server import Dispatcher
from utils import log


class ServerBase:
    """Server base for center, channel, and login servers
    """

    def __init__(self, parent, port):
        self._loop = get_event_loop()
        self._parent = parent
        self._port = port
        self._is_alive = False
        self._clients = []
        self._packet_handlers = []
        self._ready = Event(loop=self._loop)
        self._alive = Event(loop=self._loop)
        self._dispatcher = Dispatcher(self)

        self._serv_sock = socket(AF_INET, SOCK_STREAM)
        self._serv_sock.setblocking(0)
        self._serv_sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        self._serv_sock.bind(("127.0.0.1", self._port))
        self._serv_sock.listen(0)

        self.add_packet_handlers()

    def log(self, message, level=None):
        level = level or "info"
        getattr(log, level)(f"{self._name} {message}")

    @property
    def alive(self):
        return self._alive.is_set()

    async def start(self):
        self._is_alive = True
        self._alive.set()
        self._ready.set()
        self._listener = self._loop.create_task(self.listen())

    def close(self):
        self._listener.cancel()

    async def on_client_accepted(self, socket):
        client_sock = ClientSocket(socket)
        client = await getattr(self, 'client_connect')(client_sock)
        self.log(f"{self.name} Accepted <lg>{client.ip}</lg>")

        self._clients.append(client)

        # Dispatch accept packet to client and begin client socket loop
        await client.initialize()

    async def on_client_disconnect(self, client):
        self._clients.remove(client)

        self.log(f"Client Disconnected {client.ip}")

    def add_packet_handlers(self):
        import inspect

        members = inspect.getmembers(self)
        for _, member in members:
            # Register all packet handlers for inheriting server

            if (isinstance(member, PacketHandler)
                    and member not in self._packet_handlers):
                self._packet_handlers.append(member)

    async def wait_until_ready(self) -> bool:
        """Block event loop until the GameServer has started listening for clients.
        """
        return await self._ready.wait()

    async def listen(self):
        self.log(f"Listening on port <lr>{self._port}</lr>")

        while self._alive.is_set():
            client_sock, _ = await self._loop.sock_accept(self._serv_sock)
            client_sock.setblocking(0)
            client_sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
            self._loop.create_task(self.on_client_accepted(client_sock))

    @property
    def data(self):
        return self._parent.data

    @property
    def dispatcher(self):
        return self._dispatcher

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def port(self):
        return self._port

    @property
    def population(self):
        return len(self._clients)
