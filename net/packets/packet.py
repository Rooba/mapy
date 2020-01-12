from enum import Enum
from io import BytesIO

from . import CRecvOps
from utils.tools import to_string

debug_codes = [
    ('r',  ( '|', '|')),
    ('lr', ( '|', '&' )),
    ('c',  ( '~',  '~' )),
    ('lc', ( '~',  '&' )),
    ('y',  ( '#',  '#' )),
    ('ly', ('#',   '&' )),
    ('g',  ('^', '^' )),
    ('lg', ('^',  '&' )),
    ('m',  ('@',   '@' )),
    ('lm', ('@',   '&' ))
]

class DebugType(Enum):
    _byte =    0x1
    _short =   0x2
    _int =     0x4
    _long =    0x8
    _string =  0x10

class ByteBuffer(BytesIO):
    """Base class for packet write and read operations"""

    def __init__(self, initial_bytes):
        super().__init__(initial_bytes)
        self._debug_string = ""
        self._last_debug_encode = ""
        self._string_len = 0
    
    def to_debug(self, val, type_, string_len = 0):
        
        debug_type = type_

        _iter = debug_codes[type_ if type_ < 8 else type_ - 2]
        color, codes = _iter
        first, second = codes

        if not isinstance(val, bytes):
            val = (val).to_bytes(type_, 'little') if isinstance(val, int) else val.encode()

        if debug_type != 10 and self._string_len != 0:
            color = self._last_debug_encode
            first = '@'
            second = '&' if self._last_debug_encode.startswith('l') else first

            self._debug_string += to_string(val)
            self._string_len -= 1
            self._debug_string += second + " " if self._string_len == 0 else " "

        elif debug_type != 10:
            if self._last_debug_encode == color:
                color = color.strip('l') if color.startswith('l') else 'l' + color
                second = '&' if second != '&' else first

            self._debug_string += (f"--{first}{to_string(val)}{second} ")
            self._last_debug_encode = color
            return
        
        else:
            if self._string_len == 0:
                self._string_len = string_len
                self._debug_string += '--' + first

                if self._last_debug_encode == color:
                    color = color.strip('l') if color.startswith('l') else 'l' + color
                    second = first if second != '&' else '&'
                
            self._debug_string += to_string(val)
            self._string_len -= 1

            if self._string_len == 0:
                self._debug_string += second + " "
            
            else:
                self._debug_string += " "

    def encode_byte(self, byte):
        if isinstance(byte, Enum):
            byte = byte.value
        
        bytes_ = (byte).to_bytes(1, 'little')
        self.write(bytes_)
        self.to_debug(bytes_, 1)

        return self

    def encode_short(self, short):
        bytes_ = (short).to_bytes(2, 'little')
        self.write(bytes_)
        self.to_debug(bytes_, 2)
        return self

    def encode_int(self, int_):
        bytes_ = (int_).to_bytes(4, 'little')
        self.write(bytes_)
        self.to_debug(bytes_, 4)
        return self
    
    def encode_long(self, long):
        bytes_ = (long).to_bytes(8, 'little')
        self.write(bytes_)
        self.to_debug(bytes_, 8)
        return self

    def encode_buffer(self, buffer):
        self.write(buffer)
        return self
    
    def skip(self, count):
        self.write(bytes(count))
        return self

    def encode_string(self, string):
        bytes_ = (len(string)).to_bytes(2, 'little')
        self.write(bytes_)
        self.to_debug(bytes_, 2)

        for ch in string:
            self.write(ch.encode())
            self.to_debug(ch.encode(), 10, len(string))
        
        return self

    def encode_fixed_string(self, string, length):
        for i in range(13):
            if i < len(string):
                self.write(string[i].encode())
                self.to_debug(string[i].encode(), 10, length)
                continue
            
            self.encode_byte(0)
        
        return self

    def decode_byte(self):
        return (int).from_bytes(self.read(1), 'little')
    
    def decode_bool(self):
        return bool(self.decode_byte())
    
    def decode_short(self):
        return (int).from_bytes(self.read(2), 'little')

    def decode_int(self):
        return (int).from_bytes(self.read(4), 'little')
    
    def decode_long(self):
        return (int).from_bytes(self.read(8), 'little')

    def decode_buffer(self, size):
        return self.read(size)

    def decode_string(self):
        length = (int).from_bytes(self.read(2), 'little')
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
    def __init__(self, data=None, op_code=None, raw=False):

        if data == None:
            data = b''

        super().__init__(data)

        if not data:
            self.op_code = op_code
            
            if isinstance(self.op_code, int):
                self.encode_short(self.op_code)
            
            else:
                self.encode_short(self.op_code.value)
            
            return 

        if raw:
            return
        
        # For debug string, giving whether byte, short, int
        # long, or string
        seg_type = self.decode_byte()

        try:
            self.op_code = CRecvOps(self.decode_short())
        
        except ValueError:
            # Not using debug packets in client, use default
            self.seek(0)
            self.op_code = CRecvOps(self.decode_short())
            return 

        packet = Packet(op_code = self.op_code)
        i = len(data) - 3

        while i > 0:
            seg_type = self.decode_byte()

            if seg_type == 1:
                packet.encode_byte(self.decode_byte())
                i -= 2
            
            elif seg_type == 2:
                packet.encode_short(self.decode_short())
                i -= 3
            
            elif seg_type == 4:
                packet.encode_int(self.decode_int())
                i -= 5
            
            elif seg_type % 8 == 0:
                num = int(seg_type / 8)

                for _ in range(num):
                    packet.encode_long(self.decode_long())
                
                i -= 1 + (8 * num)

            elif seg_type == 10:
                str_ = self.decode_string()
                packet.encode_string(str_)
                i -= (len(str_) + 3)
        

        super().__init__(packet.getvalue())
        self.seek(2)
        self._debug_string = packet._debug_string

    @property
    def name(self):
        if isinstance(self.op_code, int):
            return self.op_code
        
        return self.op_code.name

    def to_array(self):
        return self.getvalue()

    def to_string(self):
        return to_string(self.getvalue())

    @property
    def debug_string(self):
        return self._debug_string if self._debug_string != "" else self.to_string()

    def __len__(self):
        return len(self.getvalue())

class PacketHandler:
    def __init__(self, name, callback, **kwargs):
        self.name = name
        self.callback = callback
        self.op_code = kwargs.get('op_code')

def packet_handler(op_code=None):
    def wrap(func):
        return PacketHandler(func.__name__, func, op_code=op_code)

    return wrap
    
