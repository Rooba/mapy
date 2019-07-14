from enum import Enum

from .item import ItemSlotEquip

class InventoryType(Enum):
    disposal = 0x0
    equip = 0x1
    consume = 0x2
    install = 0x3
    etc = 0x4
    cash = 0x5

class InventoryManager(list):
    def __init__(self):
        super().__init__()
        self.append(Disposal())
        self.extend([Inventory(type_, 96) for type_ in InventoryType if type_ is not InventoryType.disposal])
        
    def get(self, inventory_type):
        for inv in self:
            if inv.type == inventory_type:
                return inv

class Disposal:
    type = InventoryType.disposal

    def __init__(self):
        self._starting = []

class Inventory:
    def __init__(self, type_, slots):
        self._slots = slots
        self.type = type_
        self.items = {i: None for i in range(1, slots + 1)}
    
    def get_free_slot(self):
        for i in range(1, self._slots + 1):
            if not self.items[i]:
                return i
        
        return None

    def add(self, item, slot=None):
        if isinstance(item, ItemSlotEquip):
            free_slot = self.get_free_slot() if not slot else slot

            if free_slot:
                self.items[free_slot] = item
    