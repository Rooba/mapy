from enum import Enum


class Meta(Enum):
    def __str__(self):
        return f"{self.__class__.__name__.lower()}.{super().__str__()}"


class Schema(Meta):
    def __new__(cls, value):
        value.schema = cls.__name__.lower()
        value.primary_key = value.__dict__.get("__primary_key__")
        value.foreign_keys = value.__dict__.get("__foreign_keys__")
        value.columns = [item.lower() for item in value._member_names_]
        return value

    def __str__(self):
        return f"{self.__class__.__name__.lower()}.{super().__str__()}"

    def __getattr__(self, name):
        if name not in ("_value_"):
            return getattr(self.value, name)
        return super().__getattr__(name)

    @classmethod
    def create(cls):
        # async def create(db):
        #     schema = db.schema(cls.__name__.lower())
        #     await schema.create(skip_if_exists=False)
        #     fks = []
        #     for table in cls:
        #         t = db.table(table._name_.lower(), schema=schema)
        #         if await t.exists(): continue
        #         cols = []
        #         for c in table:
        #             primary_key = c.getattr('primary_key', False)
        #             col = Column(c._name_.lower(), c.data_type, primary_key=primary_key, **c.options)
        #             if t.foreign_keys and c.name in getattr(table, 'foreign_keys', []):
        #                 fks.append(types.ForeignKey(t, col, sql_type=c.data_type))
        #             cols.append(col)
        #         await t.create(*cols)
        #     for fkey in fks:
        #         await db.execute_transaction(fk.to_sql())

        # return create
        pass


class Table(int, Meta):
    _ignore_ = "data_type"

    def __new__(cls, data_type, options=None):
        value = len(cls.__members__) + 1
        enum_class = super().__new__(cls, value)

        enum_class._value_ = value
        enum_class.data_type = data_type

        # if data_type in ['integer', 'serial']:
        #     enum_class.data_type = types.Integer(auto_increment=data_type == 'serial')
        # elif data_type == 'smallint':
        #     enum_class.data_type = types.Integer(small=True)
        # elif data_type == 'bigint':
        #     enum_class.data_type = types.Integer(big=True)
        # elif data_type in ['varchar', 'text']:
        #     enum_class.data_type = types.String()
        # elif data_type == 'jsonb':
        #     enum_class.data_type = types.JSON()
        # elif data_type == 'double':
        #     enum_class.data_type = types.Double()
        # elif data_type == 'boolean':
        #     enum_class.data_type = types.Boolean()
        # elif data_type == 'date':
        #     enum_class.data_type = types.Date()

        # from re import search
        # if search(r'(\[\])', data_type):
        #     enum_class.data_type = types.ArraySQL(enum_class.data_type)

        enum_class.options = options if options else {}
        return enum_class


class ItemConsumeableData(Table):
    ITEM_ID = "integer"
    FLAGS = "varchar[]"
    CURES = "varchar[]"
    HP = "smallint"
    HP_PERCENTAGE = "smallint"
    MAX_HP_PERCENTAGE = "smallint"
    MP = "smallint"
    MP_PERCENTAGE = "smallint"
    MAX_MP_PERCENTAGE = "smallint"
    WEAPON_ATTACK = "smallint"
    WEAPON_ATTACK_PERCENTAGE = "smallint"
    WEAPON_DEFENSE = "smallint"
    WEAPON_DEFENSE_PERCENTAGE = "smallint"
    MAGIC_ATTACK = "smallint"
    MAGIC_ATTACK_PERCENTAGE = "smallint"
    MAGIC_DEFENSE = "smallint"
    MAGIC_DEFENSE_PERCENTAGE = "smallint"
    ACCURACY = "smallint"
    ACCURACY_PERCENTAGE = "smallint"
    AVOID = "smallint"
    AVOID_PERCENTAGE = "smallint"
    SPEED = "smallint"
    SPEED_PERCENTAGE = "smallint"
    JUMP = "smallint"
    SECONDARY_STAT = "jsonb"
    BUFF_TIME = "integer"
    PROB = "smallint"
    EVENT_POINT = "integer"
    MOB_ID = "integer"
    MOB_HP = "integer"
    SCREEN_MESSAGE = "text"
    ATTACK_INDEX = "smallint"
    ATTACK_MOB_ID = "integer"
    MOVE_TO = "integer"
    RETURN_MAP_QR = "integer"
    DECREASE_HUNGER = "smallint"
    MORPH = "smallint"
    CARNIVAL_TYPE = "smallint"
    CARNIVAL_POINTS = "smallint"
    CARNIVAL_SKILL = "smallint"
    EXPERIENCE = "integer"

    __primary_key__ = ("ITEM_ID",)


class ItemData(Table):
    ITEM_ID = "integer"
    INVENTORY = "smallint"
    PRICE = ("integer", {"default": 0})
    MAX_SLOT_QUANTITY = "smallint"
    MAX_POSSESSION_COUNT = "smallint"
    MIN_LEVEL = "smallint"
    MAX_LEVEL = ("smallint", {"default": 250})
    EXPERIENCE = "integer"
    MONEY = "integer"
    STATE_CHANGE_ITEM = "integer"
    LEVEL_FOR_MAKER = "smallint"
    NPC = "integer"
    FLAGS = ("varchar[]", {"default": "'{}'"})
    PET_LIFE_EXTEND = "smallint"
    MAPLE_POINT = "integer"
    MONEY_MIN = "integer"
    MONEY_MAX = "integer"
    EXP_RATE = "double"
    ADD_TIME = "smallint"
    SLOT_INDEX = "smallint"

    __primary_key__ = ("ITEM_ID",)


class ItemEquipData(Table):
    ITEM_ID = "integer"
    FLAGS = ("varchar[]", {"default": "'{}'"})
    EQUIP_SLOTS = ("varchar[]", {"default": "'{}'"})
    ATTACK_SPEED = ("smallint", {"default": 0})
    RUC = ("smallint", {"default": 0})
    REQ_STR = ("smallint", {"default": 0})
    REQ_DEX = ("smallint", {"default": 0})
    REQ_INT = ("smallint", {"default": 0})
    REQ_LUK = ("smallint", {"default": 0})
    REQ_FAME = ("smallint", {"default": 0})
    REQ_JOB = ("smallint[]", {"default": "'{}'"})
    HP = ("smallint", {"default": 0})
    HP_PERCENTAGE = ("smallint", {"default": 0})
    MP = ("smallint", {"default": 0})
    MP_PERCENTAGE = ("smallint", {"default": 0})
    STR = ("smallint", {"default": 0})
    DEX = ("smallint", {"default": 0})
    INT = ("smallint", {"default": 0})
    LUK = ("smallint", {"default": 0})
    HANDS = ("smallint", {"default": 0})
    WEAPON_ATTACK = ("smallint", {"default": 0})
    WEAPON_DEFENSE = ("smallint", {"default": 0})
    MAGIC_ATTACK = ("smallint", {"default": 0})
    MAGIC_DEFENSE = ("smallint", {"default": 0})
    ACCURACY = ("smallint", {"default": 0})
    AVOID = ("smallint", {"default": 0})
    JUMP = ("smallint", {"default": 0})
    SPEED = ("smallint", {"default": 0})
    TRACTION = ("double", {"default": 0})
    RECOVERY = ("double", {"default": 0})
    KNOCKBACK = ("smallint", {"default": 0})
    TAMING_MOB = ("smallint", {"default": 0})
    DURABILITY = ("integer", {"default": "'-1'::integer"})
    INC_LIGHTNING_DAMAGE = ("smallint", {"default": 0})
    INC_ICE_DAMAGE = ("smallint", {"default": 0})
    INC_FIRE_DAMAGE = ("smallint", {"default": 0})
    INC_POISON_DAMAGE = ("smallint", {"default": 0})
    ELEMENTAL_DEFAULT = ("smallint", {"default": 0})
    CRAFT = ("smallint", {"default": 0})
    SET_ID = ("integer", {"default": 0})
    ENCHANT_CATEGORY = ("smallint", {"default": 0})
    HEAL_HP = ("smallint", {"default": 0})
    SPECIAL_ID = ("integer", {"default": 0})

    __primary_key__ = "ITEM_ID"


class ItemPetData(Table):
    ITEM_ID = "integer"
    HUNGER = "smallint"
    LIFE = "smallint"
    LIMITED_LIFE = "integer"
    EVOLUTION_ITEM = "integer"
    EVOLUTION_LEVEL = "smallint"
    FLAGS = "varchar[]"

    __primary_key__ = ("ITEM_ID",)


class ItemRechargeableData(Table):
    ITEM_ID = "integer"
    UNIT_PRICE = "smallint"
    WEAPON_ATTACK = "smallint"

    __primary_key__ = "ITEM_ID"


class MapData(Table):
    MAP_ID = "integer"
    MAP_NAME = ("text", {"default": "''::text"})
    STREET_NAME = ("text", {"default": "''::text"})
    MAP_MARK = ("text", {"default": "''::text"})
    FLAGS = ("varchar[]", {"default": "'{}'"})
    MOB_RATE = ("double", {"default": 1.0})
    FIXED_MOB_CAPACITY = "smallint"
    SPAWN_MOB_INTERVAL = "smallint"
    DROP_RATE = ("double", {"default": 1.0})
    REGEN_RATE = ("double", {"default": 1.0})
    SHUFFLE_NAME = ("text", {"default": "NULL::varchar"})
    DEFAULT_BGM = ("text", {"default": "NULL::varchar"})
    EFFECT = ("text", {"default": "NULL::varchar"})
    MIN_LEVEL_LIMIT = "smallint"
    MAX_LEVEL_LIMIT = "smallint"
    TIME_LIMIT = "smallint"
    DEFAULT_TRACTION = ("double", {"default": 1})
    MAP_LTX = "smallint"
    MAP_LTY = "smallint"
    MAP_RBX = "smallint"
    MAP_RBY = "smallint"
    LP_BOTTOM = "smallint"
    LP_TOP = "smallint"
    LP_SIDE = "smallint"
    FORCED_MAP_RETURN = "integer"
    FIELD_TYPE = "smallint"
    DECREASE_HP = "integer"
    DECREASE_MP = "integer"
    DECREASE_INTERVAL = "smallint"
    DAMAGE_PER_SECOND = "smallint"
    PROTECT_ITEM = "integer"
    SHIP_KIND = "smallint"
    CONSUME_COOLDOWN = "smallint"
    LINK = "integer"
    FIELD_LIMITATIONS = ("bigint", {"default": 0})
    RETURN_MAP = "integer"
    MAP_LIMIT = "smallint"
    MAP_VERSION = "smallint"
    ON_FIRST_USER_ENTER = "text"
    ON_USER_ENTER = "text"
    DESCRIPTION = ("text", {"default": "''::text"})
    MOVE_LIMIT = "smallint"
    PROTECT_SET = "integer"
    ALLOWED_ITEM_DROP = "integer"
    DROP_EXPIRE = "smallint"
    TIME_OUT_LIMIT = "smallint"
    PHASE_ALPHA = "smallint"
    PHASE_BACKGROUND = "smallint"
    TIME_MOB_SPAWN = "smallint"

    __primary_key__ = "MAP_ID"


class MapFootholds(Table):
    MAP_ID = "integer"
    GROUP_ID = "smallint"
    ID = "smallint"
    X_1 = "smallint"
    Y_1 = "smallint"
    X_2 = "smallint"
    Y_2 = "smallint"
    DRAG_FORCE = "smallint"
    PREVIOUS_ID = "smallint"
    NEXT_ID = "smallint"
    FLAGS = "varchar[]"

    __primary_key__ = ("MAP_ID", "GROUP_ID", "ID")


class MapLife(Table):
    MAP_ID = "integer"
    LIFE_ID = "integer"
    LIFE_TYPE = "text"
    LIFE_NAME = ("text", {"default": "''::text"})
    X_POS = "smallint"
    Y_POS = "smallint"
    FOOTHOLD = "smallint"
    MIN_CLICK_POS = "smallint"
    MAX_CLICK_POS = "smallint"
    RESPAWN_TIME = "integer"
    FLAGS = ("varchar[]", {"default": "'{}'"})
    CY = "smallint"
    FACE = ("boolean", {"default": 0})
    HIDE = ("boolean", {"default": 0})

    __primary_key__ = None


class MapPortals(Table):
    MAP_ID = "integer"
    ID = "smallint"
    NAME = "text"
    X_POS = "smallint"
    Y_POS = "smallint"
    DESTINATION = "integer"
    DESTINATION_LABEL = "text"
    PORTAL_TYPE = "smallint"

    __primary_key__ = ("MAP_ID", "ID")


class MapReactors(Table):
    MAP_ID = "integer"
    REACTOR_ID = "integer"
    REACTOR_TIME = "integer"
    NAME = "text"
    X = "smallint"
    Y = "smallint"
    F = "smallint"

    __primary_key__ = ("MAP_ID", "REACTOR_ID")


class MapTimedMobs(Table):
    MAP_ID = "integer"
    MOB_ID = "integer"
    START_HOUR = "smallint"
    END_HOUR = "smallint"
    MESSAGE = "text"

    __primary_key__ = ("MAP_ID", "MOB_ID")


class MobData(Table):
    MOB_ID = "integer"
    MOB_LEVEL = "smallint"
    FLAGS = ("varchar[]", {"default": "'{}'"})
    HP = "integer"
    HP_RECOVERY = "integer"
    MP = "integer"
    MP_RECOVERY = "integer"
    EXPERIENCE = "integer"
    KNOCKBACK = "integer"
    FIXED_DAMAGE = "integer"
    EXPLODE_HP = "integer"
    LINK = "integer"
    SUMMON_TYPE = "smallint"
    DEATH_BUFF = "integer"
    DEATH_AFTER = "integer"
    TRACTION = ("double", {"default": 1.0})
    DAMAGED_BY_SKILL_ONLY = "smallint"
    DAMAGED_BY_MOB_ONLY = "integer"
    DROP_ITEM_PERIOD = "smallint"
    HP_BAR_COLOR = "smallint"
    HP_BAR_BG_COLOR = "smallint"
    CARNIVAL_POINTS = "smallint"
    PHYSICAL_ATTACK = "smallint"
    PHYSICAL_DEFENSE = "smallint"
    PHYSICAL_DEFENSE_RATE = "smallint"
    MAGICAL_ATTACK = "smallint"
    MAGICAL_DEFENSE = "smallint"
    MAGICAL_DEFENSE_RATE = "smallint"
    ACCURACY = "smallint"
    AVOID = "smallint"
    SPEED = "smallint"
    FLY_SPEED = "smallint"
    CHASE_SPEED = "smallint"
    ICE_MODIFIER = "smallint"
    FIRE_MODIFIER = "smallint"
    POISON_MODIFIER = "smallint"
    LIGHTNING_MODIFIER = "smallint"
    HOLY_MODIFIER = "smallint"
    DARK_MODIFIER = "smallint"
    NONELEMENTAL_MODIFIER = "smallint"

    __primary_key__ = "MOB_ID"


class MobSkills(Table):
    MOB_ID = "integer"
    SKILL_ID = "smallint"
    LEVEL = "smallint"
    EFFECT_AFTER = "smallint"

    __primary_key__ = ("MOB_ID", "SKILL_ID")


class PlayerSkillData(Table):
    SKILL_ID = "integer"
    FLAGS = "varchar[]"
    WEAPON = "smallint"
    SUB_WEAPON = "smallint"
    MAX_LEVEL = "smallint"
    BASE_MAX_LEVEL = "smallint"
    SKILL_TYPE = "varchar[]"
    ELEMENT = "text"
    MOB_COUNT = "text"
    HIT_COUNT = "text"
    BUFF_TIME = "text"
    HP_COST = "text"
    MP_COST = "text"
    DAMAGE = "text"
    FIXED_DAMAGE = "text"
    CRITICAL_DAMAGE = "text"
    MASTERY = "text"
    OPTIONAL_ITEM_COST = "smallint"
    ITEM_COST = "integer"
    ITEM_COUNT = "smallint"
    BULLET_COST = "smallint"
    MONEY_COST = "text"
    X_PROPERTY = "text"
    Y_PROPERTY = "text"
    SPEED = "text"
    JUMP = "text"
    STR = "text"
    WEAPON_ATTACK = "text"
    WEAPON_DEFENSE = "text"
    MAGIC_ATTACK = "text"
    MAGIC_DEFENSE = "text"
    ACCURACY = "text"
    AVOID = "text"
    HP = "text"
    MP = "text"
    PROBABILITY = "text"
    LTX = "smallint"
    LTY = "smallint"
    RBX = "smallint"
    RBY = "smallint"
    COOLDOWN_TIME = "text"
    AVOID_CHANCE = "text"
    RANGE = "text"
    MORPH = "smallint"

    __primary_key__ = "SKILL_ID"


class PlayerSkillRequirementData(Table):
    SKILL_ID = "integer"
    REQ_SKILL_ID = "integer"
    REQ_LEVEL = "smallint"

    __primary_key__ = ("SKILL_ID", "REQ_SKILL_ID")


class String(Table):
    OBJECT_ID = "integer"
    OBJECT_TYPE = "varchar"
    DESCRIPTION = "text"
    LABEL = "text"

    __primary_key__ = ("OBJECT_ID", "OBJECT_TYPE")


class RMDB(Schema):
    ITEM_CONSUMEABLE_DATA = ItemConsumeableData
    ITEM_DATA = ItemData
    ITEM_EQUIP_DATA = ItemEquipData
    ITEM_PET_DATA = ItemPetData
    ITEM_RECHARGEABLE_DATA = ItemRechargeableData
    MAP_DATA = MapData
    MAP_FOOTHOLDS = MapFootholds
    MAP_LIFE = MapLife
    MAP_PORTALS = MapPortals
    MAP_REACTORS = MapReactors
    MAP_TIMED_MOBS = MapTimedMobs
    MOB_DATA = MobData
    MOB_SKILLS = MobSkills
    PLAYER_SKILL_DATA = PlayerSkillData
    PLAYER_SKILL_REQS_DATA = PlayerSkillRequirementData
    STRING = String


class Account(Table):
    ID = "serial"
    USERNAME = "text"
    PASSWORD = "text"
    SALT = "text"
    CREATION = ("date", {"default": "CURRENT_DATE"})
    LAST_LOGIN = ("date", {"default": '"1970-01-01"::date'})
    LAST_IP = ("inet", {"default": '"0.0.0.0"::inet'})
    BAN = ("bool", {"default": 0})
    ADMIN = ("bool", {"default": 0})
    GENDER = "bool"

    __primary_key__ = ("ID",)
    # __unqiue_index__ = ("USERNAME")


class Buddies(Table):
    pass


class Character(Table):
    ID = "integer"
    ACCOUNT_ID = "integer"
    NAME = "text"
    GENDER = "bool"
    SKIN = "smallint"
    FACE = "smallint"
    HAIR = "smallint"
    PET_LOCKER = "int[]"
    LEVEL = "smallint"
    JOB = "smallint"
    STR = "smallint"
    DEX = "smallint"
    INT = "smallint"
    LUK = "smallint"
    HP = "smallint"
    MAX_HP = "smallint"
    MP = "smallint"
    MAX_MP = "smallint"
    AP = "smallint"
    SP = "smallint"
    EXP = "integer"
    MONEY = "integer"
    TEMP_EXP = "integer"
    FIELD_ID = "integer"
    PORTAL = "text"
    PLAY_TIME = "integer"
    SUB_JOB = "smallint"
    FAME = "smallint"
    EXTEND_SP = "smallint[]"
    WORLD_ID = "smallint"

    __primary_key__ = ("ID",)
    __foreign_keys__ = {"account_id": "accounts.id"}


class InventoryEquipment(Table):
    INVENTORY_ITEM_ID = "bigint"
    UPGRADE_SLOTS = "integer"
    STR = "smallint"
    DEX = "smallint"
    INT = "smallint"
    LUK = "smallint"
    HP = "integer"
    MP = "integer"
    WEAPON_ATTACK = "smallint"
    MAGIC_ATTACK = "smallint"
    WEAPON_DEFENSE = "smallint"
    MAGIC_DEFENSE = "smallint"
    ACCURACY = "smallint"
    AVOID = "smallint"
    HANDS = "smallint"
    SPEED = "smallint"
    JUMP = "smallint"
    RING_ID = "integer"
    CRAFT = "smallint"
    ATTRIBUTE = "smallint"
    LEVEL_UP_TYPE = "smallint"
    LEVEL = "smallint"
    IUC = "integer"
    GRADE = "smallint"
    EXP = "smallint"
    CHUC = "smallint"
    OPTION_1 = "smallint"
    OPTION_2 = "smallint"
    OPTION_3 = "smallint"
    SOCKET_1 = "smallint"
    SOCKET_2 = "smallint"
    LISN = "bigint"
    CUC = "smallint"
    RUC = "smallint"

    __primary_key__ = "inventory_item_id"
    __foreign_keys__ = {"INVENTORY_ITEM_ID": "inventory_items.inventory_item_id"}


class InventoryItems(Table):
    INVENTORY_ITEM_ID = "bigint"
    CHARACTER_ID = "integer"
    STORAGE_ID = "integer"
    ITEM_ID = "integer"
    INVENTORY_TYPE = "smallint"
    POSITION = "integer"
    OWNER = "text"
    PET_ID = "bigint"
    QUANTITY = "integer"
    CISN = "bigint"  # Current inventory Serial
    SN = "bigint"  # Serial Number (Would replace inventory_item_id?)
    EXPIRE = "bigint"

    __primary_key__ = "inventory_item_id"


# class InventoryPets(Table):
#     pass


# class Keymap(Table):
#     pass


# class Skills(Table):
#     pass


class Maplestory(Schema):
    ACCOUNTS = Account
    BUDDIES = Buddies
    CHARACTERS = Character
    INVENTORY_EQUIPMENT = InventoryEquipment
    INVENTORY_ITEMS = InventoryItems
    # INVENTORY_PETS      = InventoryPets
    # KEYMAP              = Keymap
    # SKILLS              = Skills
