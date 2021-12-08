from abc import ABCMeta


class Serializable(metaclass=ABCMeta):
    def __serialize__(self):
        serialized = {}
        for key, value in self.__dict__.items():
            if issubclass(value.__class__, Serializable):
                value = value.__serialize__()

            serialized[key] = value

        return serialized


class WildcardData:
    @classmethod
    def __new__(cls, *args, **kwargs):
        old_init = cls.__init__

        def _new_init_(self, *args, **kwargs):
            cleaned = {}
            for key, value in kwargs.items():
                if key not in dir(cls):
                    continue
                cleaned[key] = value
            old_init(self, *args, **cleaned)

        cls.__init__ = _new_init_
        return super(WildcardData, cls).__new__(cls)


class Inventory:
    ...
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
