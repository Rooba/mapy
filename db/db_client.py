from copy import deepcopy
import json
from typing import Union

from asyncpg import create_pool
from asyncpg.exceptions import InterfaceError
from datetime import date

from character import (
    Account as Account_,
    Character,
    FuncKey,
    SkillEntry,
    CharacterEntry,
)
from game import (
    item as Item,
    # ItemSlotBundle,
    ItemSlotEquip,
    SkillLevelData,
)
from field import Field as field, Foothold, Mob, Npc, Portal
from .schema import (
    Table,
    Query,
    Insert,
    Update,
    Schema,
    Column,
    IntColumn,
    StringColumn,
    ListArguments,
)
from .structure import RMDB, Maplestory
from utils import log, get


async def init_conn(conn):
    await conn.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )
    await conn.set_type_codec(
        "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )


DATABASE = "maplestory"
ACCOUNTS = f"{DATABASE}.accounts"
CHARACTERS = f"{DATABASE}.characters"
ITEMS = f"{DATABASE}.inventory_items"
EQUIPS = f"{DATABASE}.inventory_equips"
SKILLS = f"{DATABASE}.skills"


class DatabaseClient:
    def __init__(
        self,
        loop,
        user="postgres",
        password="",
        host="127.0.0.1",
        port=5432,
        database="postgres",
    ):

        self.loop = loop
        self.dsn = f"postgres://{user}:{password}@{host}:{port}/{database}"

        # WZ Data
        self._items = Items(self)
        self._skills = Skills(self)

    async def start(self, loop=None):
        # try:
        self.pool = await create_pool(self.dsn, loop=self.loop, init=init_conn)
        log.info("Connected to PostgreSQL Server")

        # await Maplestory.create()

    async def stop(self):
        if self.pool:
            await self.pool.close()
            self.pool.terminate()

        log.debug("Closed PostgreSQL pool")

    async def recreate_pool(self):
        log.warning("Re-Creating PostgreSQL pool")
        self.pool = await create_pool(self.dsn, loop=self.loop, init=init_conn)

    async def initialize_database(self):
        pass

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

    async def create_table(
        self, name: str, columns: list[Union[Column, str]], *, primaries=None
    ) -> Table:
        return await Table(self, name).create(columns, primaries=primaries)

    def table(self, name, *, schema: Union[str, Schema] = None) -> Table:
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
        return Characters(self)

    @property
    def field(self):
        return Field(self)

    @property
    def items(self):
        return self._items

    @property
    def skills(self):
        return self._skills


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


class QueryTable:
    @property
    def table(self):
        return self._db.table(self._table)

    def query(self, table=None):
        return self._db.query(table if table else self._table)

    @property
    def query(self):
        return self.table.query

    def insert(self, *args, **kwargs):
        return self.query.insert(*args, **kwargs)


class Account(QueryTable):
    def __init__(
        self,
        db,
        *,
        id_=None,
        username=None,
        password=None,
        creation=None,
        last_login=None,
        last_ip=None,
        ban=False,
        admin=False,
        gender=None,
        **kwargs,
    ):

        self._db = db
        self._table = ACCOUNTS

        self.id = id_ if id_ else kwargs.get("id", None)
        self.username = username
        self.password = password
        self.creation = creation
        self.last_login = last_login
        self.last_ip = last_ip
        self.ban = ban
        self.admin = admin
        self.gender = gender

        self.characters = Characters(self._db, account_id=self.id)

    async def get_account(self):
        if not self.username or self.id:
            log.error("Missing username or password to search by")

        search = {
            a: getattr(self, a)
            for a in ["id", "username", "password"]
            if hasattr(self, a) and getattr(self, a, None)
        }

        self.account = Account_(**(await self.query.where(**search).get_first()))

    @get_acc
    async def register(self):
        if self.account:
            return False

        if ret_id := await (
            self.insert(
                username=self.username,
                password=self.password,
                creation=date.today(),
                last_ip=self.last_ip,
            )
            .returning("accounts.id")
            .commit()
            .get_first()
        ):
            self.id = ret_id
            return True

        return False

    @get_acc
    async def login(self):
        if self.account is None:
            return (5, None)

        if self.account.password != self.password:
            return (4, None)

        return (0, self.account)

    async def get_entries(self, world_id=None):
        return await self.characters.get_entries(world_id=world_id)

    async def create_character(self, character):
        return await self.characters.create(character)


class Characters(QueryTable):
    def __init__(self, db, account_id=None):
        self.account_id = account_id
        self._db = db
        self._table = CHARACTERS
        self._inventories = Inventories(db)
        self._func_keys = FuncKeys(db)
        self._skills = Skills(db)

    async def get_entries(self, world_id=None):
        entries = []

        if not world_id:
            characters = await (
                self.query.where(account_id=self.account_id).order_by("id").get()
            )
        else:
            characters = await (
                self.query.where(account_id=self.account_id, world_id=world_id)
                .order_by("id")
                .get()
            )

        for character in characters:
            character = CharacterEntry(**character)

            equips = await (
                self.query(ITEMS)
                .where(
                    IntColumn("position") < 0,
                    character_id=character.id,
                )
                .get()
            )

            for item in equips:
                slot = item["position"]
                item = ItemSlotEquip(**item)
                character.equip.add(item, slot)

            entries.append(character)

        return entries

    async def load(self, character_id, client):
        character = await self.query.where(id=character_id).get_first()

        character = Character(character)
        character.client = client
        character.data = self

        await self._inventories.load(character)
        await self._func_keys.load(character)

        skills = await self.query(SKILLS).where(character_id=character.id).get()

        for skill in skills:
            level_data = await self._db.skills.get_skill_level_data(skill["id"])
            character.skills[skill["id"]] = SkillEntry(level_data=level_data, **skill)

        return character

    async def get(self, **search_by):
        character = await self.query.where(**search_by).get_first()

        return character

    async def create(self, character):
        character_data = {**character.stats.__dict__}
        character_data["account_id"] = self.account_id
        character_data.pop("id")
        inventories = character_data.pop("inventories")

        character_id = (
            await self.insert(**character_data)
            .primaries("name")
            .returning("characters.id")
            .commit()
        )

        if character_id:
            character_id = character_id[0]["id"]
            await self.update_inventory(character_id, inventories)

        return character_id

    async def update_inventory(self, character_id, inventories):
        items_columns = await self._db.table(
            "maplestory.inventory_items"
        ).columns.get_names()

        equips_columns = await self._db.table(
            "maplestory.inventory_equipment"
        ).columns.get_names()

        items = inventories.get_update()

        for item in items:
            item_data = dict()
            for column_name in items_columns:
                value = item.get(column_name)
                if value is None:
                    continue

                item_data[column_name] = value

            item_data["character_id"] = character_id

            inv_item_id = (
                await self._db.table("maplestory.inventory_items")
                .insert(**item_data)
                .primaries("inventory_item_id")
                .returning("inventory_items.inventory_item_id")
                .commit(do_update=True)
            )
            inv_item_id = inv_item_id[0]["inventory_item_id"]

            if item["inventory_type"] == 1:
                equip_data = dict()
                for column_name in equips_columns:
                    value = item.get(column_name)
                    if value is None:
                        continue

                    equip_data[column_name] = item.get(column_name)

                equip_data["inventory_item_id"] = inv_item_id

                await self._db.table("maplestory.inventory_equipment").insert(
                    **equip_data
                ).primaries("inventory_item_id").commit(do_update=True)


class Inventories:
    def __init__(self, db):
        self._db = db
        self._items_table = db.table("maplestory.inventory_items")
        self._equips_table = db.table("maplestory.inventory_equipment")

    @property
    def items_table(self):
        return deepcopy(self._items_table)

    @property
    def equips_table(self):
        return deepcopy(self._equips_table)

    async def load(self, character):
        items = self.items_table.query().where(character_id=character.id)

        items_col, equips_col = IntColumn.many(
            ("items.inventory_item_id",), ("inventory_equipment.inventory_item_id",)
        )

        equips = (
            self._db.query("maplestory.inventory_equipment", "items")
            .select("inventory_equipment.*")
            .where(equips_col.in_(items_col))
        )

        inventory = await (
            self._db.query()
            .with_(("items", items), ("equips", equips))
            .table("items")
            .inner_join("equips", "inventory_item_id")
            .get()
        )

        for item in inventory:
            inventory_type = item["inventory_type"]
            slot = item["position"]
            item = getattr(Item, Item.ItemInventoryTypes(inventory_type).name)(**item)
            character.inventories.add(item, slot)

        character.inventories.tracker.copy(*character.inventories)

    async def save(self, character):
        items = []
        equips = []

        for item in character.inventories.inventory_changes:
            item_data = {}
            equip_data = {}
            for column_name in Maplestory.INVENTORY_ITEMS.columns:
                value = item.get(column_name)
                if value is None:
                    continue

                item_data[column_name] = value

            item_data["character_id"] = character.id

            items.append(item_data)

            if item["inventory_type"] == 1:
                for column_name in Maplestory.INVENTORY_EQUIPMENT.columns:
                    value = item.get(column_name)
                    if value is None:
                        continue

                    equip_data[column_name] = item.get(column_name)
                    equip_data["position"] = item["position"]

                equips.append(equip_data)

        q = (
            await self._db.table("maplestory.inventory_items")
            .insert.row(items)
            .primaries("inventory_item_id")
            .returning("inventory_items.inventory_item_id, inventory_items.position")
            .commit(do_update=True)
        )

        if equips:
            for item in q:
                for equip in equips:
                    if item["position"] == equip["position"]:
                        equip["inventory_item_id"] = item["inventory_item_id"]
                        equip.pop("position")

            await self._db.table("maplestory.inventory_equipment").insert.rows(
                equips
            ).primaries("inventory_item_id").commit(do_update=True)


class FuncKeys(QueryTable):
    def __init__(self, db):
        self._db = db

    async def load(self, character):
        func_keys = (
            await self._db.table("maplestory.keymap")
            .query()
            .select("key", "type", "action")
            .where(character_id=character.id)
            .get()
        )

        for key in func_keys:
            character.func_keys[key["key"]] = FuncKey(key["type"], key["action"])


class Items:
    def __init__(self, db):
        self._db = db
        self._cached_items = []
        self._item_data_table = self._db.table("rmdb.item_data")

    @property
    def item_data(self):
        return self._item_data_table

    async def get_many(self, *item_ids):
        item_ids = item_ids
        pre_cached = [item for item in self._cached_items if item.item_id in item_ids]

        assert pre_cached.count() != 0

        cached_ids = set([i.item_id for i in pre_cached])

        if cached_ids == set(item_ids):
            return pre_cached

        to_cache = list(set([i for i in item_ids]) - cached_ids)

        def get_type(type_):
            return ListArguments(
                [i for i, id in enumerate(to_cache) if int(id / 1000000) == type_]
            )

        inv_type = {
            1: get_type(1),
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

            query = self._db.query("rmdb.item_data").select(*RMDB.ITEM_DATA.columns)

            if v is not None:
                query.inner_join(f"rmdb.item_{v}_data", "item_id").where(
                    IntColumn("item_id") in specific
                )

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

        item_type = int(item_id / 1000000)

        query = await (self.query("rmdb.item_data"))

        if item_type == 1:
            query.inner_join("rmdb.item_equip_data", "item_id").where(item_id=item_id)

        fetched_item = await query.get_first()
        cleaned_item = {}

        for key, value in fetched_item.items():
            if value is not None:
                cleaned_item[key] = value

        item = getattr(Item, Item.ItemInventoryTypes(item_type).name)(**cleaned_item)
        self._cached_items.append(item)
        return item


class Skills:
    def __init__(self, db):
        self._db = db
        self._cached_skills = {}

    async def get_skill_level_data(self, skill_id):
        skill_level_data = self._cached_skills.get(skill_id, None)

        if skill_level_data:
            return skill_level_data

        level_data = (
            await self._db.table("rmdb.player_skill_data")
            .query()
            .where(skill_id=skill_id)
            .get_first()
        )

        skill_level_data = SkillLevelData(**level_data)
        self._cached_skills[skill_id] = skill_level_data

        return skill_level_data


class Field:
    def __init__(self, db):
        self._db = db

    async def get(self, map_id):
        _field = field(map_id)

        portals = (
            await self._db.table("rmdb.map_portals").query().where(map_id=map_id).get()
        )

        for portal in portals:
            _field.portals.add(Portal(**portal))

        footholds = (
            await self._db.table("rmdb.map_footholds")
            .query()
            .where(map_id=map_id)
            .get()
        )

        for foothold in footholds:
            _field.footholds.add(Foothold(**foothold))

        life = self._db.query("rmdb.map_life").where(map_id=map_id)

        life_column = IntColumn("life_id")
        mob_column = IntColumn("mob_id")

        mobs = (
            self._db.query("rmdb.mob_data", "life")
            .select("mob_data.*", "life.life_type", "mob_data.mob_id", distinct=True)
            .where(
                StringColumn("life.life_type").__eq__("mob"),
                mob_column.in_(life_column),
            )
        )

        all_life = (
            self._db.query()
            .with_(("life", life), ("mobs", mobs))
            .table("life")
            .left_join("mobs", "life_type")
        )

        all_life = await all_life.get()

        for life_obj in all_life:
            if life_obj["life_type"] == "mob":
                _field.mobs.add(Mob(**life_obj))
            elif life_obj["life_type"] == "npc":
                _field.npcs.add(Npc(**life_obj))

        return _field
