from abc import ABCMeta
from enum import EnumMeta, IntFlag, Flag
from typing import Any, Generic, TypeVar


class Serializable(metaclass=ABCMeta):
    def __serialize__(self):
        serialized = {}
        for key, value in self.__dict__.items():
            if issubclass(value.__class__, Serializable):
                value = value.__serialize__()

            serialized[key] = value

        return serialized


class WildcardData:
    def __new__(cls, *args, **kwargs):
        old_init = cls.__init__

        def _new_init_(self, *_args, **_kwargs):
            cleaned = {}
            for key, value in _kwargs.items():
                if key not in dir(cls):
                    continue
                cleaned[key] = value
            old_init(self, *_args, **cleaned)

        cls.__init__ = _new_init_
        return super(WildcardData, cls).__new__(cls)


class Inventory(metaclass=ABCMeta):
    def __init__(self):
        self.items = {}

    def add(self, item, slot=None):
        return NotImplemented


class BITN(int):
    ...


class BIT1(int):
    ...


BIT = TypeVar("BIT", BIT1, BITN)


class FlagType(Generic[BIT]):
    _name_ = ""
    __dict__ = {
        "_member_map_": {},
        "_member_names_": [],
        "_name_": "",
        "_value_": 0,
        "__members__": {},
        "__name__": "",
        "_members_": [],
    }

    def __str__(self):
        return self._name_


class BitMask(FlagType, Flag):
    """Subclassable Enum, linters throw a fit not really sure what to do about that"""

    __original_call__ = EnumMeta.__call__
    setattr(EnumMeta, "__original_call__", __original_call__)
    __orig_getattr__ = getattr(EnumMeta, "__getattr__")
    setattr(EnumMeta, "__orig_getattr__", getattr(EnumMeta, "__getattr__"))

    def __new__(cls, *args):
        if args[0] != 0 and "NONE" not in cls._member_map_.keys():
            if "NONE" not in cls._member_map_.keys():
                none = cls(0)
                none._name_ = "NONE"
                none._value_ = 0
                cls.NONE = none
                cls._member_map_["NONE"] = none
                cls._value2member_map_ |= {0: none}
                cls._member_names_.append("NONE")

        return super(BitMask).__init__(args[0])

    def __getattr__(self, name):
        if (
            isinstance(self, type)
            and name not in BitMask.__orig_getattr__(self, "_member_names_")
            and (issubclass(self, BitMask) or issubclass(self, IntFlag))
        ):
            new_val = len(self._member_names_)
            new = self(new_val)
            new._name_ = name
            # setattr(cls, name, new_val)
            self._member_map_[name] = new
            self._value2member_map_[new_val] = new
            self._members_.append(new)
            self._member_names_.append(name)
            return new

        return getattr(EnumMeta, "__orig_getattr__")(self, name)

    def __call__(
        self, value, names=None, *, module=None, qualname=None, _type=None, start=1
    ):
        _names = names
        if isinstance(self, type) and not issubclass(self, BitMask):
            return self.__class__.__original_call__(
                self,  # type: ignore
                value,
                _names,  # type: ignore
                module=module,
                qualname=qualname,
                type=_type,
                start=start,
            )

        if isinstance(self, type) and (
            (issubclass(self, BitMask) and names is not None)
            or not issubclass(self, BitMask)
        ):
            return getattr(EnumMeta, "__original_call__")(self, value, names=_names)

        return self.__new__(self, value)

    setattr(EnumMeta, "__call__", __call__)
    setattr(EnumMeta, "__getattr__", __getattr__)

    def __str__(self):
        print(self)
        return self._name_

    def __repr__(self):
        print(self)
        return self._name_


class ObjectPool:
    def __init__(self, field):
        self.field = field
        self.cache = {}
        self.uid_base = 1000

    @property
    def new_uid(self):
        self.uid_base += 1
        return self.uid_base

    def add(self, value):
        value.obj_id = self.new_uid
        self.cache[value.obj_id] = value

    def remove(self, key):
        return self.cache.pop(key)

    def clear(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key, None)

    def __enumerator__(self):
        return (obj for obj in self.cache.values())

    def __iter__(self):
        return (obj for obj in self.cache.values())

    def __aiter__(self):
        return self.__iter__()
