from json import dumps
from urllib.robotparser import RequestRate
from sanic import Sanic, Blueprint, json
from sanic.config import Config
from sanic.blueprint_group import BlueprintGroup
from re import compile

mem_re = compile(r"^[A-Z_]+$")

http_api = Sanic("__mapy__")
http_api.enable_websocket()
http_api.asgi = True
api = Blueprint(name="api", url_prefix="api/")
ws = Blueprint(name="ws", url_prefix="ws/")
api_group = BlueprintGroup("")
api_group.extend([api, ws])


@api.websocket("/ws/status/")
async def ws_stats(request, ws):
    _center = request.app.ctx.center
    login = _center._login
    _stat = {
        "uptime": _center.uptime,
        "population": _center.population,
        "login_server": {
            "alive": login.alive if login else 0,
            "port": login.port if login else 0,
            "population": login.population if login else 0,
        },
        "game_servers": {
            world.name: {
                f"{i}": {
                    "alive": channel.alive,
                    "port": channel.port,
                    "population": channel.population,
                }
                for i, channel in enumerate(world.channels, 1)
            }
            for world in _center.worlds.values()
        },
    }
    if ws.data_received:
        content = await ws.recv_burst()
        print(content)
    await ws.send(dumps(_stat))
    await ws.close()


@api.get("/status/")
async def statistics(request):
    _center = request.app.ctx.center
    login = _center._login
    _stat = {
        "uptime": _center.uptime,
        "population": _center.population,
        "login_server": {
            "alive": login.alive if login else 0,
            "port": login.port if login else 0,
            "population": login.population if login else 0,
        },
        "game_servers": {
            world.name: {
                i: {
                    "alive": channel.alive,
                    "port": channel.port,
                    "population": channel.population,
                }
                for i, channel in enumerate(world.channels, 1)
            }
            for world in _center.worlds.values()
        },
    }
    return json(_stat)


http_api.blueprint(api_group)
