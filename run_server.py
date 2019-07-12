from asyncio import get_event_loop, Task
from sys import argv
import logging

from server import CenterServer, WvsLogin, WvsGame

logging.basicConfig(level=logging.DEBUG)
loop = get_event_loop()
# loop.set_debug(True)

if len(argv) > 1:
    server_option = argv[1]

else:
    server_option = input("Which Server do we start? : \n [ center | login | game ] ")

cls = {
    'center': CenterServer,
    'login': WvsLogin,
    'game': WvsGame,
}.get(server_option)

if not cls:
    exit("Decalre server: run [ center | login | game ]")

Server = cls(loop)

try:
    loop.run_forever()

except KeyboardInterrupt:
    print("Shutting down %s", Server.name)

finally:
    for task in Task.all_tasks():
        task.cancel()

    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
