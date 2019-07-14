from asyncio import create_task, get_event_loop, wait_for, sleep
from socket import socket, SO_REUSEADDR, SOL_SOCKET, AF_INET, SOCK_STREAM
import logging

log = logging.getLogger(__name__)

from net.packets.packet import Packet
from net.packets.opcodes import InterOps

class ClientListener(object):
    """Server connection listener for incoming client socket connections
        
    Parameters
    -----------
    parent: :class:`ServerBase`
        The running server
    connection: Tuple[str, int]
        The connection IP and Port the socket listens on

    Attribtues
    ----------
    is_alive: bool
        The servers current alive status

    """
    
    def __init__(self, parent, connection):
        self._connection = connection
        self._parent = parent
        self._loop = parent._loop if parent._loop else get_event_loop()

        self._serv_sock = socket(AF_INET, SOCK_STREAM)
        self._serv_sock.setblocking(0)
        self._serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._serv_sock.bind(self._connection)
        self._serv_sock.listen(0)

    def is_alive(self):
        return self._parent.is_alive

    async def _listen(self):
        log.info("Listening on port %s", self._connection[1])
        
        while self.is_alive:
            client_sock, _ = await self._loop.sock_accept(self._serv_sock)
            client_sock.setblocking(0)

            create_task(self._parent.on_client_accepted(client_sock))
