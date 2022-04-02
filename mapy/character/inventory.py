from typing import Any
from mapy.common import Inventory as _Inventory, InventoryType
from mapy.game import item as Item
from .inventory import Inventory


class InventoryManager:

    def __init__(self, character):
        self._character = character
        self.tracker = Tracker()
        self.inventories: dict[int, Inventory] = {}

        for i in range(1, 6):
            self.inventories[i] = Inventory(InventoryType(i), 96)

    def __iter__(self):
        return ((inv_type, inv.items)
                for inv_type, inv in self.inventories.items())

    @property
    def updates(self):
        return self.tracker.inventory_changes

    def get(self, inventory_type):

        if isinstance(inventory_type, InventoryType):
            return self.inventories[inventory_type.value]

        elif isinstance(inventory_type, int):
            return self.inventories.get(inventory_type)

        return None

    def add(self, item: Item.ItemSlotBase, slot=0):
        item_type = int(item.item_id / 1000000)
        inventory: Inventory = self.inventories[item_type]

        item_ = inventory.add(item, slot)

        if not item_:
            return

        slot = item_[0]
        item_ = item_[1]

        self.tracker.insert(slot, item_)


class Tracker:

    def __init__(self):
        self.type = InventoryType.TRACKER
        self._starting = []

        # Only update this on stat improvement,
        # movement, or new item added
        self._items = {i: {} for i in range(1, 6)}

    def insert(self, item, slot):
        self._items[int(item.item_id / 1000000)][slot] = item

    @property
    def inventory_changes(self):
        return [{
            **item.__dict__, "inventory_type": inv_type,
            "position": slot
        }
                for inv_type, inventory in self._items.items()
                for slot, item in inventory.items()]

    # def get_update(self):
    #     return [{**item.__dict__,
    #              'inventory_type': inv_type,
    #              'position': slot
    #              } for inv_type, inventory in self._items.items()
    #             for slot, item in inventory.items()]

    def get_throwaway(self):
        throwaway = []

        for _, inv in self._items.items():
            for _, item in inv.items():
                if item is None or item.inventory_item_id in self._starting:
                    continue

                throwaway.append(item.inventory_item_id)

        return throwaway

    def copy(self, *inventories):
        for _, inventory in inventories:
            for _, item in inventory.items():
                if item:
                    self._starting.append(item.inventory_item_id)


class Inventory(_Inventory):

    def __init__(self, type_, slots):
        self._unique_id = None
        self.type = type_
        self.items: dict[int, Any] = {i: None for i in range(1, slots + 1)}
        self._slots = slots

    def __getitem__(self, key):
        return self.items.get(key)

    def __iter__(self):
        return (item for item in self.items)

    def get_free_slot(self):
        for i in range(1, self._slots + 1):
            if not self.items[i]:
                return i

        return None

    def add(self,
            item: Item.ItemSlotBase,
            slot=None) -> tuple[int, Item.ItemSlotBase | None]:
        items = None

        if isinstance(item, Item.ItemSlotEquip):
            free_slot = self.get_free_slot() if not slot else slot

            if free_slot:
                self.items[free_slot] = item
                items = (free_slot, item)

        elif isinstance(item, Item.ItemSlotBundle):
            # Get Slot with same item_id and not max bundle
            # or insert into free slot
            pass

        if not items:
            return (0, None)

        return items

    @property
    def slots(self):
        return self._slots

    def encode(self, packet):
        for slot, item in self.items.items():
            if not item:
                continue

            packet.encode_byte(slot)
            item.encode(packet)

        packet.encode_byte(0)
