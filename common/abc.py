from abc import ABCMeta
from random import randint

class Serializable(metaclass=ABCMeta):
    def __serialize__(self):
        serialized = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Serializable):
                value = value.__serialize__()

            serialized[key] = value

        return serialized
    
class Inventory:
    pass
    # def add(self, item, slot=None):
    #     if isinstance(item, ItemSlotEquip):
    #         free_slot = self.get_free_slot() if not slot else slot

    #         if free_slot:
    #             self.items[free_slot] = item
    #             items = ((free_slot, item),)

    #         else:
    #             items = None

    #     elif isinstance(item, ItemSlotBundle):
    #         # Get Slot with same item_id and not max bundle
    #         # or insert into free slot
    #         pass

    #     return items