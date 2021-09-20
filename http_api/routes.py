from aiohttp.web import RouteDef, RouteTableDef, json_response


class Base(RouteTableDef):
    def __init_subclass__(cls):
        cls._handlers = []
        for k, v in cls.__dict__.items():
            if k.startswith("_"):
                continue
            cls._handlers.append(v)

    def __new__(cls, http_serv):
        new_cls = super().__new__(cls)
        return new_cls

    def __init__(self):
        super().__init__()
        for handler in self._handlers:
            method = handler._method
            path = handler._path
            kwargs = handler._kwargs
            self._items.append(
                RouteDef(
                    method,
                    path,
                    getattr(self, handler.__name__),
                    kwargs
                )
            )


def route(method, path, **kwargs):
    def wrap(handler):
        handler._method = method
        handler._path = path
        handler._kwargs = kwargs
        return handler
    return wrap


class Routes(Base):
    def __init__(self, http_serv):
        self._http = http_serv
        self._server = http_serv.server
        super().__init__()

    @route("GET", "/")
    async def get_status(self, request):
        resp = {
            'uptime': self._server.uptime,
            'population': self._server.population,
            'login_server': {
                'alive': self._server.login.alive,
                'port': self._server.login.port,
                'population': self._server.login.population
            },
            'game_servers': {
                world.name: {
                    i: {
                        'alive': channel.alive,
                        'port': channel.port,
                        'population': channel.population
                    } for i, channel in enumerate(world.channels, 1)
                } for world in self._server.worlds.values()
            }
        }

        return json_response(resp)
