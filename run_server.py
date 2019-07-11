from asyncio import get_event_loop
from sys import argv
import logging

logging.basicConfig(level=logging.DEBUG)
loop = get_event_loop()
# loop.set_debug(True)

from server import CenterServer, WvsLogin, WvsGame

if len(argv) > 1:
    server_option = argv[1]

else:
    server_option = input("Which Server do we start? : \n[center|login|game] ")

cls = {
    'center': CenterServer,
    'login': WvsLogin,
    'game': WvsGame,
}.get(server_option)

if not cls:
    exit("Decalre server: run center|login")

Server = cls(loop)

try:
    loop.run_forever()

except KeyboardInterrupt:
    print(f"Shutting down {Server.name}")

finally:
    for task in loop.all_tasks():
        task.cancel()

    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
