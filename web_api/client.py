from aiohttp import ClientSession
from loguru import logger

from client.entities import Character, ItemSlotEquip
from common.constants import HTTP_API_ROUTE
from utils import fix_dict_keys


class Route:
    def __init__(self, method, route, 
        data=None, params=None, json=None):
        self._method = method
        self._route = route
        self._data = data
        self._params = params
        self._json = json


class HTTPClient:
    def __init__(self, loop=None):
        self._loop = loop
        self._host = HTTP_API_ROUTE

    async def request(self, route, content_type="json"):
        session = ClientSession(loop=self._loop)

        kwargs = {}
        url = self._host + route._route

        if route._data:
            kwargs['data'] = route._data

        if route._params:
            kwargs['params'] = route._params
        
        if route._json:
            kwargs['json'] = route._json

        r = await session.request(route._method, url, **kwargs)

        try:
            if r.status is 200:
                if content_type == 'json':
                    data = await r.json()

                elif content_type == 'image':
                    data = await r.read()

                else:
                    data = await r.text()

                return data

            return None

        except Exception as e:
            (e)

        finally:
            await r.release()
            await session.close()

    ##
    # Main Data Provider
    ##

    async def is_username_taken(self, character_name):
        response = await self.request(
            Route("GET", "/character/name/" + character_name))

        return response['resp']

    async def login(self, username, password):
        route = Route(
            "POST", "/login",
            data={
                'username': username,
                'password': password,
            }
        )

        response = await self.request(route)
        return response

    async def get_characters(self, account_id, world_id=None):
        if not world_id:
            url = f"/account/{account_id}/characters"

        else:
            url = f"/account/{account_id}/characters/{world_id}"

        response = fix_dict_keys(await self.request(Route("GET", url)))

        return [Character.from_data(**character) for character in response['characters']]

    async def create_new_character(self, account_id, character:Character):
        route = Route(
            "POST", f"/account/{account_id}/character/new",
            json=character.__serialize__()
        )

        response = await self.request(route)

        return response['id']

    ##
    # Static Data Provider
    ##

    async def get_item(self, item_id):
        route = Route("GET", f"/item/{item_id}")
        response = await self.request(route)

        item = ItemSlotEquip(**response)
        return item
