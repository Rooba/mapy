from ..common.enum import InventoryType
from .character_stats import CharacterStats
from .inventory import Inventory


class CharacterEntry:
    def __init__(self, **stats):
        self._stats = CharacterStats(**stats)
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

        packet.encode_int(0 if not equipped.get(-111) else equipped[-111].item_id)

        # for pet_id in self.pet_ids:
        for pet_id in range(3):
            packet.encode_int(pet_id)
