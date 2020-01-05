from asyncio import sleep

from dataclasses import dataclass, is_dataclass


def find(predicate, seq):
    for element in seq:
        if predicate(element):
            return element
    return None

def get(iterable, **attrs):
    def predicate(elem):
        for attr, val in attrs.items():
            nested = attr.split('__')
            obj = elem
            for attribute in nested:
                obj = getattr(obj, attribute)

            if obj != val:
                return False
        return True

    return find(predicate, iterable)


def filter_out_to(func, iters, out):
    new = []

    for item in iters:
        if func(item):
            new.append(item)
        else:
            out.append(item)

    return new


def first_or_default(list_, f):
    return next((val for val in list_ if f(val)), None)


def fix_dict_keys(dict_):
    copy = dict(dict_)

    for key, value in copy.items():
        if key.isdigit():
            value = dict_.pop(key)
            key = int(key)

        if isinstance(value, dict):
            dict_[key] = fix_dict_keys(value)

        else:
            dict_[key] = value

    return dict_


def to_string(bytes_):
    return ' '.join(
        [bytes_.hex()[i:i+2].upper() for i in range(0, len(bytes_.hex()), 2)])


async def wakeup():
    while True:
        await sleep(.01)


def nested_dataclass(*args, **kwargs):
    def wrapper(cls):
        cls = dataclass(cls, **kwargs)
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            for name, value in kwargs.items():
                field_type = cls.__annotations__.get(name, None)

                if is_dataclass(field_type) and isinstance(value, dict):
                    new_obj = field_type(**value)
                    kwargs[name] = new_obj

            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper


class Manager(list):
    def get(self, search):
        return first_or_default(self, search)

    def first_or_default(self, func):
        return next((val for val in self if func(val)), None)
