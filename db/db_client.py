import json

from asyncio import create_task
from asyncpg import create_pool
from asyncpg.exceptions import InterfaceError
from datetime import date

from client.entities import Account as Acc, Character, item as Item
from utils import log, get
from .schema import Table, Query, Insert, Update, Schema, IntColumn, ListArguments
from .structure import RMDB


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
        
        # WZ Data
        self._items = Items(self)
    
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

    @property
    def characters(self):
        return Characters(self, None)

    @property
    def items(self):
        return self._items


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
        
        self._db = db
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
        self.characters = Characters(self._db, id)

    async def get_account(self):
        accounts = self._db.table('maplestory.accounts')

        if self.username:
            account = await accounts.query.where(username=self.username).get_first()
        
        elif self.id:
            account = await accounts.query.where(id=self.id).get_first()
        
        if not account:
            self.account = None

        self.account = Acc(**account)

    @get_acc
    async def register(self):
        accounts = self._db.table('maplestory.accounts')

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

    async def get_characters(self, world_id=None):
        return await self.characters.load(world_id=world_id)

    async def create_character(self, character):
        return await self.characters.create(character)


class Characters:
    def __init__(self, db, account_id):
        self._db = db
        self.account_id = account_id
    
    async def load(self, world_id=None):
        
        ret = []
        if not world_id:
            characters = await self._db.table('maplestory.characters').query()\
                .where(account_id=self.account_id).order_by('id').get()
        else:
            characters = await self._db.table('maplestory.characters').query()\
                .where(account_id=self.account_id, world_id=world_id).order_by('id').get()

        for character in characters:
            character = Character(**character)

            items = self._db.query('maplestory.inventory_items')\
                .where(character_id=character.id)\
            
            items_item_id_column = IntColumn('items.inventory_item_id')
            equip_item_id_column = IntColumn('inventory_equipment.inventory_item_id')

            equips = self._db.query('maplestory.inventory_equipment', 'items')\
                .select("inventory_equipment.*")\
                    .where(equip_item_id_column.in_(items_item_id_column))
    
            inventory = await self._db.query().\
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

    async def get(self, **search_by):
        character = await self._db.table('maplestory.characters')\
            .query()\
                .where(**search_by)\
                    .get_first()
        
        return character

    async def create(self, character):
        character_data = {**character.__dict__}
        character_data['account_id'] = self.account_id
        character_data.pop('id')
        inventories = character_data.pop('inventories')

        character_id = await self._db.table('maplestory.characters')\
            .insert(**character_data)\
                .primaries('name')\
                    .returning('characters.id')\
                        .commit()

        if character_id:
            character_id = character_id[0]['id']
            await self.update_inventory(character_id, inventories)

        return character_id
        
    async def update_inventory(self, character_id, inventories):
        items_columns = await self._db.table('maplestory.inventory_items').columns.get_names()

        equips_columns = await self._db.table('maplestory.inventory_equipment').columns.get_names()

        items = inventories.get_update()

        for item in items:
            item_data = dict()
            for column_name in items_columns:
                value = item.get(column_name)
                if value is None:
                    continue
                
                item_data[column_name] = value
            
            item_data['character_id'] = character_id

            inv_item_id = await self._db.table('maplestory.inventory_items')\
                .insert(**item_data)\
                    .primaries('inventory_item_id')\
                        .returning('inventory_items.inventory_item_id')\
                            .commit(do_update=True)
            inv_item_id = inv_item_id[0]['inventory_item_id']
            
            if item['inventory_type'] == 1:
                equip_data = dict()
                for column_name in equips_columns:
                    value = item.get(column_name)
                    if value is None:
                        continue

                    equip_data[column_name] = item.get(column_name)

                equip_data['inventory_item_id'] = inv_item_id

                await self._db.table('maplestory.inventory_equipment')\
                    .insert(**equip_data)\
                        .primaries('inventory_item_id')\
                            .commit(do_update=True)


class Items:
    def __init__(self, db):
        self._db = db
        self._cached_items = []

    async def get_many(self, *item_ids):
        item_ids = list(item_ids)
        pre_cached = [item for item in self._cached_items if item.item_id in item_ids]
        if len(pre_cached) == len(item_ids):
            return pre_cached
        
        if len(pre_cached):
            for item in pre_cached:
                if item.item_id in item_ids:
                    item_ids.remove(item.item_id)

        def get_type(type_):
            copy = item_ids[:]
            return ListArguments([item_ids.pop(i) for i, id in enumerate(copy) if int(id / 1000000) is type_])
        
        inv_type = {
            1: 'equip',
        #     20: 'consumeable',
        #     21: 'rechargeable',
        #     3: None,
        #     4: None,
        #     50: 'pet',
        #     51: None
        }.get()

        items = []

        for k, v in inv_type.items():
            specific = get_type(k)
            if not len(specific):
                continue
            
            query = self._db.query('rmdb.item_data')\
                .select(*RMDB.ITEM_DATA.columns)

            if v is not None:
                query.inner_join(f'rmdb.item_{v}_data', 'item_id')\
                    .where(IntColumn('item_id') in specific)
            
            fetched_items = await query.get()

            for fetched_item in fetched_items:
                cleaned_item = {}
                for k, v in fetched_item.items():
                    if v:
                        cleaned_item[k] = v
                
                item = getattr(Item, Item.ItemInventoryTypes(k).name)(**cleaned_item)
                items.append(item)
                self._cached_items.append(item)
        
        items.extend(pre_cached)
        return items

    async def get(self, item_id):
        pre_cached = get(self._cached_items, item_id=item_id)
        if pre_cached:
            return pre_cached

        query = self._db.query('rmdb.item_data')
        item_type = int(item_id / 1000000)

        if item_type is 1:
            query.inner_join('rmdb.item_equip_data', 'item_id')\
                .where(item_id=item_id)
        
        fetched_item = await query.get_first()
        cleaned_item = {}

        for key, value in fetched_item.items():
            if value is not None:
                cleaned_item[key] = value

        item = getattr(Item, Item.ItemInventoryTypes(item_type).name)(**cleaned_item)
        self._cached_items.append(item)
        return item

