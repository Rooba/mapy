from common import abc
from utils import filter_out_to

from . import item as Item
from .inventory import InventoryManager, InventoryType


def f(a):
    return [0 for _ in range(a)]


class Character(abc.Serializable):
    def __init__(self, **data):

        self.id = data.get('id', None)
        self.name = data.get('name', "Mapler")
        self.world_id = data.get('world_id', 0)

        self.gender = data.get('gender', 0)
        self.skin = data.get('skin', 0)
        self.face = data.get('face', 20001)
        self.hair = data.get('hair', 30003)

        self.level = data.get('level', 10)
        self.job = data.get('job', 0)
        self.str = data.get('str', 20)
        self.dex = data.get('dex', 12)
        self.int = data.get('int', 11)
        self.luk = data.get('luk', 11)

        self.hp = data.get('hp', 50)
        self.m_hp = data.get('m_hp', 50)
        self.mp = data.get('mp', 5)
        self.m_mp = data.get('m_mp', 5)

        self.ap = data.get('ap', 0)
        self.sp = data.get('sp', 0)
        self.extend_sp = data.get('extend_sp', f(10))

        self.exp = data.get('exp', 0)
        self.money = data.get('money', 0)
        self.fame = data.get('fame', 0)

        self.temp_exp = data.get('temp_exp', 0)
        self.field_id = data.get('pos_map', 100000000)
        self.portal = data.get('portal', 0)
        self.play_time = data.get('play_time', 0)
        self.sub_job = data.get('sub_job', 0)
        self.pet_locker = data.get('pet_locker', f(3))
        # self.pet_ids = f(3)

        self.inventories = InventoryManager()

    @staticmethod
    def from_data(**data):
        character = Character(**data)

        for key, inv in data.get('inventories').items():
            key = int(key)
            for position, item_data in inv.items():
                position = int(position)

                item = getattr(Item, Item.ItemInventoryTypes(key).name)(**item_data)

                character.inventories.add(item, position)

        character.inventories.tracker\
            .copy(*character.inventories)

        return character

    def encode_stats(self, packet):
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
        packet.encode_short(self.str)
        packet.encode_short(self.dex)
        packet.encode_short(self.int)
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

    def encode_look(self, packet):

        packet.encode_byte(self.gender)
        packet.encode_byte(self.skin)
        packet.encode_int(self.face)
        packet.encode_byte(0)
        packet.encode_int(self.hair)

        inventory = self.inventories.get(InventoryType.equip)
        equipped = {}

        for index, item in inventory:
            if index < 0:
                equipped[index] = inventory[index]

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
