from aiohttp import ClientSession
import logging

log = logging.getLogger(__name__)


class Route:
    def __init__(self, method, route, data=None, params=None):
        self._method = method
        self._route = route
        self._data = data
        self._params = params

class HTTPClient:
    def __init__(self, loop = None):
        self._loop = loop
        self._host = "https://map.hypermine.com:54545"
    
    async def request(self, route):
        session = ClientSession(loop = self._loop)
        kwargs = {}
        url = self._host + route._route

        if route._data:
            kwargs['data'] = route._data
        
        if route._params:
            kwargs['params'] = route._params

        r = await session.request(route._method, url, **kwargs)

        try:
            if r.status is 200:
                if r.headers['content-type'] == 'application/json':
                    data = await r.json()

                elif r.headers['content-type'].startswith('image'):
                    data = await r.read()

                else:
                    data = await r.text()

                return data
            
            return None
        
        except Exception as e:
            log.info(e)
        
        finally:
            await r.release()

    async def is_username_taken(self, character_name):
        response = await self.request(Route("GET", "/characters/name/" + character_name))

        return response['resp']

    async def post_login(self, username, password):
        route = Route("POST", "/account/login", 
            data = {
                'username': username, 
                'password':password,
            })

        response = await self.request(route)
        
        return response

