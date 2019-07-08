from aiohttp import ClientSession
from asyncio import get_event_loop

class Route:
    def __init__(self, method, route, data=None, params=None):
        self._method = method
        self._route = route
        self._data = data
        self._params = params

class HTTPClient:
    def __init__(self, loop = None):
        self._loop = loop if loop else get_event_loop()
        self._session = ClientSession(loop = self._loop)
        self._host = "https://map.hypermine.com:54545"
    
    async def request(self, route):
        kwargs = {}

        url = self._host + route._route

        if route._data:
            kwargs['data'] = route._data
        
        if route._params:
            kwargs['params'] = route._params

        r = await self._session.request(route._method, url, **kwargs)

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
            print(e)
        
        finally:
            await r.release()

    async def is_username_taken(self, character_name):
        response = await self.request(Route("GET", f"/characters/name/{character_name}"))

        return response['resp']

    async def post_login(self, username, password):
        route = Route("POST", "/account/login", 
            data = {
                'username': username, 
                'password':password,
            })

        response = await self.request(route)
        
        return response

