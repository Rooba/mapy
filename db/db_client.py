import json

from asyncio import create_task
from asyncpg import create_pool
from asyncpg.exceptions import InterfaceError
from datetime import date

from client.entities import Account as Acc, Character, item as Item
from utils import log
from .schema import Table, Query, Insert, Update, Schema, IntColumn


async def init_conn(conn):
    await conn.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")
    await conn.set_type_codec(
        "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")


class DatabaseClient:

    def __init__(self, 
                loop, 
                user="postgres", 
                password="", 
                host="127.0.0.1", 
                port=5432, 
                database="postgres"):
        
        self.loop = loop
        self.dsn = f"postgres://{user}:{password}@{host}:{port}/{database}"
    
    async def start(self, loop=None):
        # try:
        self.pool = await create_pool(
            self.dsn,
            loop=self.loop,
            init=init_conn
        )
        log.info('Connected to postgresql server')

    async def stop(self):
        if self.pool:
            await self.pool.close()
            self.pool.terminate()
        
        log.debug("Closed PostgreSQL pool")

    async def recreate_pool(self):
        log.warning('Re-creating closed database pool.')
        self.pool = await create_pool(
            self.dsn, 
            loop=self.loop, 
            init=init_conn
        )

    async def execute_query(self, query, *args):
        result = []

        async with self.pool.acquire() as conn:
            stmt = await conn.prepare(query)
            records = await stmt.fetch(*args)

            for record in records:
                result.append(record)
        
        return result

    async def execute_transaction(self, query, *query_args):
        result = []
        try:
            async with self.pool.acquire() as conn:
                stmt = await conn.prepare(query)

                if any(isinstance(x, (set, tuple)) for x in query_args):
                    async with conn.transaction():
                        for query_arg in query_args:
                            async for rcrd in stmt.cursor(*query_arg):
                                result.append(rcrd)
                
                else:
                    async with conn.transaction():
                        async for rcrd in stmt.cursor(*query_args):
                            result.append(rcrd)
                
                return result
        
        except InterfaceError:
            await self.recreate_pool()
            return await self.execute_transaction(query, *query_args)

    async def create_table(self, name, columns, *, primaries=None):
        return await Table(self, name).create(columns, primaries=primaries)
    
    def table(self, name):
        return Table(name, self)

    def query(self, *tables):
        return Query(self, *tables)

    def insert(self, table):
        return Insert(self, table)

    def update(self, table):
        return Update(self, table)

    def schema(self, name):
        return Schema(self, name)
    
    def account(self, **kwargs):
        return Account(self, **kwargs)


def get_acc(fn):
    def wrapper(self, **kwargs):
        async def wrapped():
            await self.get_account()
            return await fn(self)
        return wrapped()
    return wrapper

def get_chars(fn):
    def wrapper(self, **kwargs):
        async def wrapped():
            await self.get_account()
            return await fn(self, **kwargs)
        return wrapped()
    return wrapper


class Account:
    def __init__(self, db, *, id=None, username=None, password=None,
                 creation=None, last_login=None, last_ip=None, ban=False,
                 admin=False, gender=None):
        
        self.db = db
        self.id = id
        self.username = username
        self.password = password
        self.creation = creation
        self.last_login = last_login
        self.last_ip = last_ip
        self.ban = ban
        self.admin = admin
        self.gender = gender

        # Should probably change `maplestory` to a constant var
        # as some may have a differently named schema
        self.characters = Characters(self.db, id)

    async def get_account(self):
        accounts = self.db.table('maplestory.accounts')

        if self.username:
            account = await accounts.query.where(username=self.username).get_first()
        
        elif self.id:
            account = await accounts.query.where(id=self.id).get_first()
        
        if not account:
            self.account = None

        self.account = Acc(**account)

    @get_acc
    async def register(self):
        accounts = self.db.table('maplestory.accounts')

        if not self.account:
            await accounts.insert(
                username=self.username, 
                password=self.password,
                creation=date.today(),
                last_ip=self.last_ip)\
                    .commit()
            
            return True
        return False

    @get_acc
    async def login(self):
        if not self.account:
            return (5, None)

        if self.account.password != self.password:
            return (4, None)
        
        return (0, self.account)

    @get_acc
    async def get_characters(self, world_id=None):
        characters = await self.characters.load(world_id=world_id)

        return characters


class Characters:
    def __init__(self, db, account_id):
        self.db = db
        self.account_id = account_id
    
    async def load(self, world_id=None):
        
        ret = []
        if not world_id:
            characters = await self.db.table('maplestory.characters').query()\
                .where(account_id=self.account_id).order_by('id').get()
        else:
            characters = await self.db.table('maplestory.characters').query()\
                .where(account_id=self.account_id, world_id=world_id).order_by('id').get()

        for character in characters:
            character = Character(**character)

            items = self.db.query('maplestory.inventory_items')\
                .where(character_id=character.id)\
                
            equips = self.db.query('maplestory.inventory_equipment', 'items')\
                .select("inventory_equipment.*")\
                    .where(IntColumn('inventory_equipment.inventory_item_id')\
                        .in_(IntColumn('items.inventory_item_id')))
    
            inventory = await self.db.query().\
                with_(('items', items), ('equips', equips))\
                    .table('items').inner_join('equips', 'inventory_item_id').get()

            for item in inventory:
                inventory_type = item['inventory_type']
                slot = item['position']
                item = getattr(Item, Item.ItemInventoryTypes(inventory_type).name)(**item)
                character.inventories.add(item, slot)
            
            character.inventories.tracker\
                .copy(*character.inventories)
            
            ret.append(character)
        
        return ret

    async def create(self, character):
        pass
