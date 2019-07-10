from asyncio import create_task, get_event_loop
from socket import socket, SO_REUSEADDR, SOL_SOCKET, AF_INET, SOCK_STREAM
from typing import Tuple
import logging

log = logging.getLogger(__name__)

from net.packets.packet import Packet
from net.packets.opcodes import InterOps

class ClientListener(object):
    """Server connection listener for incoming client socket connections
        
    Attributes
    -----------
    is_alive : bool
        Server alive status

    """
    
    def __init__(self, parent, connection: Tuple[str, int]):
        self._connection = connection

        self._parent = parent

        self._loop = parent._loop if parent._loop else get_event_loop()
        self._serv_sock = socket(AF_INET, SOCK_STREAM)
        self._serv_sock.setblocking(0)
        self._serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._serv_sock.bind(connection)
        self._serv_sock.listen(5)

    def is_alive(self):
        return self._parent.is_alive
    
    # def broadcast(self, clients, message):
    #     '''
    #     Send Message to list of client objects
    #     '''
    #     for client in clients:
    #         client.send(message)

    async def _listen(self):
        print(f"Listening on port {self._connection[1]}")

        while self.is_alive:
            client_sock, _ = await self._loop.sock_accept(self._serv_sock)
            client_sock.setblocking(0)

            create_task(self._parent.on_client_accepted(client_sock))
