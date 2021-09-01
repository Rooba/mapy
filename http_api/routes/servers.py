from aiohttp.web import RouteTableDef, json_response, Response


routes = RouteTableDef()

#TODO: Add check for request referer is pixelmarket.net

@routes.route("GET", "/")
async def get_status(request):
    
    resp = {
        'uptime': request.app.server.uptime,
        'population': request.app.server.population,
        'LoginServer': {
            'alive': request.app.server.login.is_alive,
            'port': request.app.server.login.port,
            'population': request.app.server.login.population
        },
        'GameServers': {}
    }

    for _, world in request.app.server.worlds.items():
        resp['GameServers'][world.name] = {}
        for i, channel in enumerate(world.channels, 1):
            resp['GameServers'][world.name][i] = {
                'alive': channel.is_alive,
                'port': channel.port,
                'population': channel.population
            }

    return json_response(resp)

def setup(client):
    return routes