from attrs import define, field

from ..client import WvsGameClient
from ..constants import (PERMANENT, InventoryType, StatModifiers,
                         is_extend_sp_job)
from ..cpacket import CPacket
from ..packet import ByteBuffer
from ..tools import Random
from .field import Field, FieldObject
from .inventory import Inventory, InventoryManager


class MapleCharacter(FieldObject):

    def __init__(self, stats: dict | None = None):
        super().__init__()
        self._client: WvsGameClient | None = None
        self._data = None

        if not stats:
            stats = {}

        self._field: None | Field = None
        self.stats = Stats(**stats)
        self.inventories: InventoryManager = InventoryManager(self)
        self.func_keys = FuncKeys(self)
        self.modify = PlayerModifiers(self)
        self.skills = {}
        self.random = Random()

        self.map_transfer = [0, 0, 0, 0, 0]
        self.map_transfer_ex = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.monster_book_cover_id = 0

    @property
    def id(self):
        return self.stats.id

    @property
    def field_id(self):
        if self._field:
            return self._field.id
        return -1

    @property
    def field(self):
        return self._field

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def equip_inventory(self) -> Inventory:
        return self.inventories.get(1) or Inventory(1, 96)

    @property
    def consume_inventory(self) -> Inventory:
        return self.inventories.get(2) or Inventory(2, 96)

    @property
    def install_inventory(self) -> Inventory:
        return self.inventories.get(3) or Inventory(3, 96)

    @property
    def etc_inventory(self) -> Inventory:
        return self.inventories.get(4) or Inventory(4, 96)

    @property
    def cash_inventory(self) -> Inventory:
        return self.inventories.get(5) or Inventory(5, 96)

    def encode_entry(self, packet):
        ranking = False

        self.stats.encode(packet)
        self.encode_look(packet)
        packet.encode_byte(0)
        packet.encode_byte(0)

        if ranking:
            packet.skip(16)

    def encode(self, packet):
        packet.encode_long(-1 & 0xFFFFFFFF)
        packet.encode_byte(0)  # combat orders
        packet.encode_byte(0)

        self.stats.encode(packet)
        packet.encode_byte(100)  # Buddylist capacity
        packet.encode_byte(False)
        packet.encode_int(self.stats.money)

        self.encode_inventories(packet)
        self.encode_skills(packet)
        self.encode_quests(packet)
        self.encode_minigames(packet)
        self.encode_rings(packet)
        self.encode_teleports(packet)
        # self.encode_monster_book(packet)
        self.encode_new_year(packet)
        packet.encode_short(0)
        # self.encode_area(packet)
        packet.encode_short(0)
        packet.encode_short(0)

    def encode_inventories(self, packet):
        packet.encode_byte(self.equip_inventory.slots)
        packet.encode_byte(self.consume_inventory.slots)
        packet.encode_byte(self.install_inventory.slots)
        packet.encode_byte(self.etc_inventory.slots)
        packet.encode_byte(self.cash_inventory.slots)

        packet.encode_int(0)
        packet.encode_int(0)

        equipped = {}

        for index, item in self.equip_inventory.items.items():
            if index < 0:
                equipped[index] = self.equip_inventory[index]

        stickers, eqp_normal = {}, {}

        if equipped.get(-11):
            eqp_normal[-11] = equipped.pop(-11)

        for index, item in equipped.items():
            if index > -100 and equipped.get(index - 100):
                eqp_normal[index] = item

            else:
                new_index = index + 100 if index < -100 else index
                stickers[new_index] = item

        inv_equip = {
            slot: item
            for slot, item in self.equip_inventory.items.items() if slot >= 0
        }
        dragon_equip = {
            slot: item
            for slot, item in self.equip_inventory.items.items()
            if slot >= -1100 and slot < -1000
        }
        mechanic_equip = {
            slot: item
            for slot, item in self.equip_inventory.items.items()
            if slot >= -1200 and slot < -1100
        }

        for inv in [
                eqp_normal, stickers, inv_equip, dragon_equip, mechanic_equip
        ]:
            for slot, item in inv.items():
                if not item:
                    continue

                packet.encode_short(abs(slot))
                item.encode(packet)

            packet.encode_short(0)

        self.consume_inventory.encode(packet)
        self.install_inventory.encode(packet)
        self.etc_inventory.encode(packet)
        self.cash_inventory.encode(packet)

    def encode_skills(self, packet):
        packet.encode_short(len(self.skills))
        for _, skill in self.skills.items():
            skill.encode(packet)

            if False:
                packet.encode_int(
                    skill.mastery_level)  # is skill needed for mastery

        packet.encode_short(0)

    def encode_quests(self, packet):
        packet.encode_short(0)

        packet.encode_short(0)

    def encode_minigames(self, packet):
        packet.encode_short(0)

    def encode_rings(self, packet):
        packet.encode_short(0)
        packet.encode_short(0)
        packet.encode_short(0)

    # Maybe needs to not be filled by default
    def encode_teleports(self, packet):
        for _ in range(5):
            packet.encode_int(0)

        for _ in range(10):
            packet.encode_int(0)

    def encode_monster_book(self, packet):
        packet.encode_int(self.monster_book_cover_id)
        packet.encode_byte(0)

        packet.encode_short(0)

    def encode_new_year(self, packet):
        packet.encode_short(0)

    def encode_area(self, packet):
        packet.encode_short(0)

    def encode_look(self, packet):
        packet.encode_byte(self.stats.gender)
        packet.encode_byte(self.stats.skin)
        packet.encode_int(self.stats.face)
        packet.encode_byte(0)
        packet.encode_int(self.stats.hair)

        inventory: Inventory = self.inventories.get(InventoryType.EQUIP)
        equipped = {}

        for index in inventory.items:
            if index < 0:
                equipped[index] = inventory.items[index]

        stickers, unseen = {}, {}

        for index, item in equipped.items():
            if index > -100 and equipped.get(index - 100):
                unseen[index] = item

            else:
                new_index = index + 100 if index < -100 else index
                stickers[new_index] = item

        for inv in [stickers, unseen]:
            for index, item in inv.items():
                packet.encode_byte(index * -1).encode_int(item.item_id)

            packet.encode_byte(0xFF)

        packet.encode_int(
            0 if not equipped.get(-111) else equipped[-111].item_id)

        # for pet_id in self.pet_ids:
        for pet_id in range(3):
            packet.encode_int(pet_id)

    async def send_packet(self, packet):
        if not self._client:
            raise ConnectionError

        await self._client.send_packet(packet)


class CharacterEntry:

    def __init__(self, **stats):
        self._stats = Stats(**stats)
        self._equip = Inventory(InventoryType.EQUIP, 96)

    @property
    def id(self):
        return self._stats.id

    @property
    def stats(self):
        return self._stats

    @property
    def equip(self):
        return self._equip

    def encode(self, packet):
        ranking = False

        self._stats.encode(packet)
        self.encode_look(packet)
        packet.encode_byte(0)  # VAC
        packet.encode_byte(ranking)

        if ranking:
            packet.skip(16)

    def encode_look(self, packet):
        packet.encode_byte(self.stats.gender)
        packet.encode_byte(self.stats.skin)
        packet.encode_int(self.stats.face)
        packet.encode_byte(0)
        packet.encode_int(self.stats.hair)

        equipped = {}

        for index, item in self.equip.items.items():
            if index < 0:
                equipped[index] = self.equip[index]

        stickers, eqp_normal = {}, {}

        if equipped.get(-11):
            eqp_normal[-11] = equipped.pop(-11)

        for index, item in equipped.items():
            if index > -100 and equipped.get(index - 100):
                eqp_normal[index] = item

            else:
                new_index = index + 100 if index < -100 else index
                stickers[new_index] = item

        for inv in [stickers, eqp_normal]:
            for slot, item in inv.items():
                packet.encode_byte(abs(slot))
                packet.encode_int(item.item_id)

            packet.encode_byte(0xFF)

        packet.encode_int(
            0 if not equipped.get(-111) else equipped[-111].item_id)

        # for pet_id in self.pet_ids:
        for pet_id in range(3):
            packet.encode_int(pet_id)


@define
class FuncKey:
    type: int
    action: int


class FuncKeys:

    def __init__(self, character):
        self._parent = character
        self._func_keys = {}

    def __setitem__(self, key, value):
        self._func_keys[key] = value

    def __getitem__(self, key):
        return self._func_keys.get(key, FuncKey(0, 0))


class Skills(dict):

    def __init__(self, parent):
        self._parent = parent

    async def cast(self, skill_id):
        skill = self.get(skill_id)

        if not skill:
            return False

        await self._parent.modify.stats(hp=self._parent.stats.hp - 1,
                                        mp=self._parent.stats.mp - 1)

        # if skill.level_data.buff_time > 0:
        #     await self._parent.buffs.remove(skill.id)

        #     buff = Buff(skill.id)
        #     buff.generate(skill.level_data)

        #     await self._parent.buff.add(buff)

        return True


def default_extend_sp():
    return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def default_pet_locker():
    return [0, 0, 0]


@define
class Stats(object):
    id: int = 0
    name: str = ""
    world_id: int = 0

    gender: int = 0
    skin: int = 0
    face: int = field(default=20001)
    hair: int = field(default=30003)
    level: int = field(default=1)
    job: int = 0

    _str: int = field(default=4)
    dex: int = field(default=4)
    _int: int = field(default=4)
    luk: int = field(default=4)
    hp: int = field(default=50)
    m_hp: int = field(default=50)
    mp: int = field(default=5)
    m_mp: int = field(default=5)

    ap: int = 0
    sp: int = 0
    extend_sp: list[int] = field(factory=lambda: list(bytearray(10)))

    exp: int = 0
    money: int = 0
    fame: int = 0
    temp_exp: int = 0

    field_id: int = field(default=100000000)
    portal: int = 0
    play_time: int = 0
    sub_job: int = 0
    pet_locker: list[int] = field(factory=lambda: list(bytearray(3)))

    def encode(self, packet) -> None:
        packet.encode_int(self.id)
        packet.encode_fixed_string(self.name, 13)
        packet.encode_byte(self.gender)
        packet.encode_byte(self.skin)
        packet.encode_int(self.face)
        packet.encode_int(self.hair)

        for sn in self.pet_locker:
            packet.encode_long(sn)

        packet.encode_byte(self.level)
        packet.encode_short(self.job)
        packet.encode_short(self._str)
        packet.encode_short(self.dex)
        packet.encode_short(self._int)
        packet.encode_short(self.luk)
        packet.encode_int(self.hp)
        packet.encode_int(self.m_hp)
        packet.encode_int(self.mp)
        packet.encode_int(self.m_mp)
        packet.encode_short(self.ap)

        # if player not evan
        packet.encode_short(self.sp)
        # else
        # packet.encode_byte(len(self.extend_sp))

        # for i, sp in enumerate(self.extend_sp):
        #     packet.encode_byte(i)
        #     packet.encode_byte(sp)

        packet.encode_int(self.exp)
        packet.encode_short(self.fame)
        packet.encode_int(self.temp_exp)
        packet.encode_int(self.field_id)
        packet.encode_byte(self.portal)
        packet.encode_int(self.play_time)
        packet.encode_short(self.sub_job)


class StatModifier:

    def __init__(self, character_stats):
        self._modifiers = []
        self._stats = character_stats

    @property
    def modifiers(self):
        return self._modifiers

    @property
    def flag(self):
        _flag = 0
        for mod in self._modifiers:
            _flag |= mod.value
        return _flag

    def alter(self, **stats):
        for key, val in stats.items():
            modifier = StatModifiers[key.upper()]
            self._modifiers.append(modifier)
            setattr(self._stats, key, val)

    def encode(self, packet):
        packet.encode_int(self.flag)

        for modifier in StatModifiers:
            if modifier not in self._modifiers:
                continue

            if modifier is StatModifiers.SP:
                if is_extend_sp_job(self._stats.job):
                    packet.encode_byte(0)
                else:
                    packet.encode_short(self._stats.sp)
            else:
                getattr(packet, f"encode_{modifier.encode}")(
                    packet, getattr(self._stats, modifier.name.lower()))


class PlayerModifiers:

    def __init__(self, character):
        self._parent = character

    async def stats(self, *, excl_req=True, **stats):
        modifier = StatModifier(self._parent.stats)
        modifier.alter(**stats)

        if modifier.modifiers:
            await self._parent.send_packet(
                CPacket.stat_changed(modifier, excl_req))


@define(kw_only=True)
class SkillEntry(object):
    id: int = int()
    level: int = int()
    mastery_level: int = int()
    max_level: int = int()
    expiration: int = PERMANENT
    level_data: list = field(factory=lambda: list())

    def encode(self, packet):
        packet.encode_int(self.id)
        packet.encode_int(self.level)
        packet.encode_long(PERMANENT)  # skill.expiration
