from asyncio import get_event_loop
from sys import argv, stderr

from server import CenterServer, WvsLogin, WvsGame

loop = get_event_loop()

if len(argv) > 1:
    server_option = argv[1]

else:
    server_option = input(
        "Which Server do we start? : \n [ center | login | game ] ")

cls = {
    'center': CenterServer,
    'login': WvsLogin,
    'game': WvsGame,
}.get(server_option)


if not cls:
    exit("Decalre server: run [ center | login | game ]")

server = cls()
server.run()
