from asyncio import get_event_loop
from sys import argv

from server.server import ServerApp

loop = get_event_loop()

ServerApp.run()
