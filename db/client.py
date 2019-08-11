import json

from asyncio import create_task
from asyncpg import create_pool
from asyncpg.exceptions import InterfaceError
from datetime import datetime

from utils import log
from .schema import Table, Query, Insert, Update, Schema


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

    async def create_table(self, name, columns, 
                            *, primaries=None):
        return await Table(self, name)\
            .create(columns, primaries=primaries)
    
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
    
    @property
    def account(self):
        return Account(self)


class Account:
    def __init__(self, db):
        self.db = db
        self.accounts = db.table('maplestory.accounts')
        self.characters = db.table('maplestory.characters')

    async def get_account_by_username(self, username, password=None):
        account = await self.accounts.query.where(username=username).get()
        return dict(account[0])

    async def register(self, username, password, ip):
        exists = await self.get_account_by_username(username)
        
        if not exists:
            await self.accounts.insert(
                username=username, 
                password=password,
                creation=datetime.now(),
                last_ip=ip)\
                    .commit()

    async def login(self, username, password):
        account = await self.get_account_by_username(username)

        if not account:
            return (5, {})

        if account['password'] != password:
            return (4, {})

        return (0, account)
