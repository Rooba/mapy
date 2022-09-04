from enum import Enum
from io import BytesIO
from struct import pack, unpack
from types import MethodType
from typing import Any, Callable, Coroutine
from typing import Type, TypeAlias, TypeVar, ParamSpec

from .opcodes import CRecvOps, CSendOps, OpCode
from .tools import to_string


WvsCenter = TypeVar("WvsCenter")
_WT = TypeVar("_WT", bound=WvsCenter)
P_ = ParamSpec("P_")

# Junk codes for colorizing incoming packets from custom client
debug_codes = [
    ("r", ("|", "|")),
    ("lr", ("|", "&")),
    ("c", ("~", "~")),
    ("lc", ("~", "&")),
    ("y", ("#", "#")),
    ("ly", ("#", "&")),
    ("g", ("^", "^")),
    ("lg", ("^", "&")),
    ("m", ("@", "@")),
    ("lm", ("@", "&")),
]


class DebugType(Enum):
    _byte = 0x1
    _short = 0x2
    _int = 0x4
    _long = 0x8
    _string = 0x10


class ByteBuffer(BytesIO):
    """Base class for packet write and read operations"""

    def encode(self, _bytes):
        self.write(_bytes)
        return self

    def encode_byte(self, value):
        if isinstance(value, Enum):
            value = value.value

        self.write(bytes([value]))
        return self

    def encode_short(self, value):
        self.write(pack("H", value))
        return self

    def encode_int(self, value):
        self.write(pack("I", value))
        return self

    def encode_long(self, value):
        self.write(pack("Q", value))
        return self

    def encode_buffer(self, buffer):
        self.write(buffer)
        return self

    def skip(self, count):
        self.write(bytes(count))
        return self

    def encode_string(self, string):
        self.write(pack("H", len(string)))

        for ch in string:
            self.write(ch.encode())

        return self

    def encode_fixed_string(self, string: str, length=13):
        self.write(pack(f"{length+1}s", string))

        return self

    def encode_hex_string(self, string: str):
        string = string.strip(" -")
        self.write(bytes.fromhex(string))
        return self

    def decode_byte(self):
        return self.read(1)[0]

    def decode_bool(self):
        return bool(self.decode_byte())

    def decode_short(self):
        return unpack("H", self.read(2))[0]

    def decode_int(self):
        return unpack("I", self.read(4))[0]

    def decode_long(self):
        return unpack("Q", self.read(8))[0]

    def decode_buffer(self, size):
        return self.read(size)

    def decode_string(self):
        length = self.decode_short()
        string = ""

        for _ in range(length):
            string += self.read(1).decode()

        return string


class Packet(ByteBuffer):
    """Packet class use in all send / recv opertions

    Parameters
    ----------
    data: bytes
        The initial data to load into the packet
    op_code: :class:`OpCodes`
        OpCode used to encode the first short onto the packet
    op_codes: :class:`OpCodes`
        Which enum to try to get the op_code from

    """

    def __init__(self, data: bytes | None = None, op_code=None, raw=False):
        self.op_code = OpCode

        if data:
            super().__init__(data)

        else:
            super().__init__()

            if isinstance(op_code, type(None)):
                return

            self.op_code = op_code

            if isinstance(self.op_code, int):
                self.encode_short(self.op_code)
            elif isinstance(self.op_code, (CSendOps, CRecvOps)):
                self.encode_short(self.op_code.value)

        if not raw and data:
            self.op_code = CRecvOps(self.decode_short())

    @property
    def name(self):
        if isinstance(self.op_code, int):
            return self.op_code

        elif isinstance(self.op_code, (CSendOps, CRecvOps)):
            return self.op_code.name

    def to_array(self):
        return self.getvalue()

    def to_string(self):
        return to_string(self.getvalue())

    def __len__(self):
        return len(self.getvalue())


class PacketHandler:
    def __init__(self, name, callback, **kwargs):
        self.name = name
        self.callback = callback
        self.op_code = kwargs.get("op_code")


def packet_handler(
    op_code=None,
) -> Coroutine[MethodType, Any, Coroutine[Packet, Any, Any]]:
    def wrap(func: Callable[P_, Coroutine]):

        return PacketHandler(func.__name__, func, op_code=op_code)

    return wrap
