from common import abc
from utils import filter_out_to, Random, MapPos

from . import item as Item
from .character_stats import CharacterStats
from .inventory import InventoryManager, InventoryType


class Character(abc.Serializable):
    def __init__(self, **data):
        self.stats = CharacterStats(**data)
        self.position = MapPos()

        self.inventories = InventoryManager()
        self.func_keys = []
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
        return self.stats.field_id

    @property
    def equip_inventory(self):
        return self.inventories.get(1)

    @property
    def consume_inventory(self):
        return self.inventories.get(2)

    @property
    def install_inventory(self):
        return self.inventories.get(3)

    @property
    def etc_inventory(self):
        return self.inventories.get(4)

    @property
    def cash_inventory(self):
        return self.inventories.get(5)

    def encode(self, packet):
        packet.encode_long(-1 & 0xFFFFFFFF)
        packet.encode_byte(0) # combat orders
        packet.encode_byte(0)

        self.stats.encode(packet)
        packet.encode_byte(100) # Buddylist capacity
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

        inv_equip = {slot: item for slot, item in self.equip_inventory.items.items() if slot >= 0}
        equipped = {slot: item for slot, item in self.equip_inventory.items.items() if slot >= -100 and slot < 0}
        equipped2 = {slot: item for slot, item in self.equip_inventory.items.items() if slot >= -1000 and slot < -100}
        dragon_equip = {slot: item for slot, item in self.equip_inventory.items.items() if slot >= -1100 and slot < -1000}
        mechanic_equip = {slot: item for slot, item in self.equip_inventory.items.items() if slot >= -1200 and slot < -1100}
        
        for inv in [equipped, equipped2, inv_equip, dragon_equip, mechanic_equip]:
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
                packet.encode_int(skill.mastery_level) # is skill needed for mastery
            
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
        for i in range(5):
            packet.encode_int(0)
        
        for i in range(10):
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
