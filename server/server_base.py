from asyncio import get_event_loop, create_task, Event, ensure_future, Task, wait_for
import signal
from sys import stderr
from functools import wraps
from loguru._logger import Logger
from loguru import logger
from re import search, compile, sub

from common.constants import HOST_IP, CENTER_PORT, USE_DATABASE, USE_HTTP_API
from net.client import ClientSocket
from net.packets.packet import PacketHandler
from net.server import Dispatcher, ClientListener
from utils.tools import wakeup
from utils import log
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

        self._name = name
        self.setup_logger()
        self._ready = Event(loop=self._loop)
        self._center = None
        self.is_alive = False
        self._clients = []
        self._packet_handlers = []
        self._dispatcher = Dispatcher(self)
        self.add_packet_handlers()

    def setup_logger(self):
        logger.remove()

        def main_formatter(record):
            repl_str = log.make_string(record['message'])
            string = f"<lg>[</lg><level>{record['level']:^12}</level><lg>]</lg> <r>[</r>{self._name}<r>]</r> <level>{repl_str}</level>"
            return string + "\n"

        logger.add(stderr, filter=log.filter_packets, colorize=True, format=main_formatter, diagnose=True)

        def in_packet_formatter(record):
            match_packet = search(r"(?P<opcode>[A-Za-z0-9\._]+)\s(?P<ip>[0-9\.]+)\s(?P<packet>[A-Z0-9\-&\^\|\#@~\s]*)", record['message'])
            matches = [*match_packet.group(1, 2, 3)]
            matches[2] = log.make_string(matches[2])

            string = f"<lg>[</lg><level>{'INPACKET':^12}</level><lg>]</lg> <r>[</r>{self._name}<r>]</r> "
            string += f"<r>[</r><level>{matches[0]}</level><r>]</r> <g>[</g>{matches[1]}<g>]</g> <w>{matches[2]}</w>"
            return string + "\n"
        
        def out_packet_formatter(record):
            match_packet = search(r"(?P<opcode>[A-Za-z0-9\._]+)\s(?P<ip>[0-9\.]+)\s(?P<packet>[A-Z0-9\-&\^\|\#@~\s]*)", record['message'])
            matches = [*match_packet.group(1, 2, 3)]
            matches[2] = log.make_string(matches[2])

            string = f"<lg>[</lg><level>{'OUTPACKET':^12}</level><lg>]</lg> <r>[</r>{self._name}<r>]</r> "
            string += f"<r>[</r><level>{matches[0]}</level><r>]</r> <g>[</g>{matches[1]}<g>]</g> <w>{matches[2]}</w>"
            return string + "\n"

        logger.level('INPACKET', 50, color="<c>")
        logger.add(stderr, colorize=True, level="INPACKET", filter=log.filter_bound_in, format=in_packet_formatter)
        
        logger.level('OUTPACKET', 50, color="<lm>")
        logger.add(stderr, colorize=True, level="OUTPACKET", filter=log.filter_bound_out, format=out_packet_formatter)

    def run(self, port=None, listen=False):
        loop = self._loop

        try:
            loop.add_signal_handler(signal.SIGINT, loop.stop)
            loop.add_signal_handler(signal.SIGTERM, loop.stop)
        except NotImplementedError:
            pass

        def stop_loop_on_completion(f):
            loop.stop()

        future = loop.create_task(self.start(port, listen))
        future.add_done_callback(stop_loop_on_completion)

        try:
            loop.run_forever()

        except KeyboardInterrupt:
            logger.warning('Received signal to terminate event loop')

        finally:
            future.remove_done_callback(stop_loop_on_completion)
            loop.run_until_complete(loop.shutdown_asyncgens())
            logger.warning(f"Closed Server {self.name}")

    async def start(self, port, listen):
        if USE_HTTP_API:
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

        logger.info(f"Accepted {maple_client.ip}")

        self._clients.append(maple_client)
        await maple_client.initialize()

    async def on_client_disconnect(self, client):
        self._clients.remove(client)
        
        logger.info(f"Client Disconnected {client.ip}")

    def add_packet_handlers(self):
        import inspect

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
    def name(self):
        return self._name