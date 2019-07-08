import asyncio
from sys import argv
# import logging

# logging.basicConfig(level=logging.DEBUG)

from common.constants import SECRET_KEY
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

loop = asyncio.get_event_loop()
# loop.set_debug(True)

Server = cls(loop, SECRET_KEY)

try:
    loop.run_forever()

except KeyboardInterrupt:
    print(f"Shutting down {Server.name}")

finally:
    for task in asyncio.Task.all_tasks():
        task.cancel()

    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
