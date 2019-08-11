from typing import Union

from common import abc
from common.enum import InventoryType
from . import item as Item


class InventoryManager(abc.Serializable):
    def __init__(self):
        self.tracker = Tracker()
        self.inventories = {}

        for i in range(1, 6):
            self.inventories[i] = Inventory(InventoryType(i), 96)

    def __iter__(self):
        return ((item[0], item[1].items) for item in self.inventories.items())

    def __serialize__(self):
        return self.tracker.__serialize__()

    def get(self, inventory_type):
        
        if isinstance(inventory_type, InventoryType):
            return self.inventories[inventory_type.value]

        elif isinstance(inventory_type, int):
            return self.inventories.get(inventory_type)
        
        return None

    def add(self, item, slot=0):
        item_type = int(item.item_id / 1000000)
        inventory = self.inventories[item_type]

        slots = inventory.add(item, slot)

        for slot, item in slots:
            self.tracker.insert(item, slot)


class Tracker(abc.Serializable):
    def __init__(self):
        self.type = InventoryType.tracker
        self._starting = []

        # Only update this on stat improvement, 
        # movement, or new item added
        self.items = {i: {} for i in range(1, 6)}

    def __serialize__(self):
        tracker = {
            'insert_update': {}
        }

        # Update on item removal or do on logout?
        tracker['throwaway'] = self.get_throwaway()

        for _, inventory in self.items.items():
            for index, item in inventory.items():
                tracker['insert_update'][index] = item.__dict__

        return tracker

    def insert(self, item, slot):
        self.items[int(item.item_id / 1000000)][slot] = item

    def get_throwaway(self):
        throwaway = []

        for _, inv in self.items.items():
            for _, item in inv.items():
                if not item:
                    continue
                
                if item.inventory_item_id in self._starting:
                    continue
                
                throwaway.append(item.inventory_item_id)

        return throwaway

    def copy(self, *inventories):
        for _, inventory in inventories:
            for _, item in inventory.items():
                if item:
                    self._starting.append(item.inventory_item_id)


class Inventory(abc.Inventory):
    def __init__(self, type_, slots):
        self.type = type_
        self.items = {i: None for i in range(1, slots + 1)}
        self._slots = slots

    def __getitem__(self, key):
        return self.items.get(key)

    def __iter__(self):
        return (item for item in self.items.items())

    def get_free_slot(self):
        for i in range(1, self._slots + 1):
            if not self.items[i]:
                return i

        return None

    def add(self, item, slot=None):
        if isinstance(item, Item.ItemSlotEquip):
            free_slot = self.get_free_slot() if not slot else slot

            if free_slot:
                self.items[free_slot] = item
                items = ((free_slot, item),)

            else:
                items = None

        elif isinstance(item, Item.ItemSlotBundle):
            # Get Slot with same item_id and not max bundle
            # or insert into free slot
            pass

        return items
