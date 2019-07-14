from enum import Enum
from io import BytesIO

from utils.tools import to_string

class ByteBuffer(BytesIO):
    def encode_byte(self, byte):
        if isinstance(byte, Enum):
            byte = byte.value
        
        self.write((byte).to_bytes(1, 'little'))
        return self

    def encode_short(self, short):
        self.write((short).to_bytes(2, 'little'))
        return self

    def encode_int(self, int_):
        self.write((int_).to_bytes(4, 'little'))
        return self
    
    def encode_long(self, long):
        self.write((long).to_bytes(8, 'little'))
        return self

    def encode_string(self, string):
        self.write((len(string)).to_bytes(2, 'little'))

        for ch in string:
            self.write(ch.encode())
        
        return self

    def encode_fixed_string(self, string, length):
        for i in range(13):
            if i < len(string):
                self.write(string[i].encode())
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

    def decode_string(self):
        length = (int).from_bytes(self.read(2), 'little')
        string = ""

        for _ in range(length):
            string += self.read(1).decode()

        return string
    


class Packet(ByteBuffer):
    def __init__(self, data=None, op_code=None, op_codes=None):
        self.op_codes = op_codes

        if data == None:
            data = b''
        
        super().__init__(data)

        if not data:
            self.op_code = op_code
            
            if isinstance(self.op_code, int):
                self.encode_short(self.op_code)
            
            else:
                self.encode_short(self.op_code.value)
                
            
        else:
            self.op_code = self.op_codes(self.decode_short())

    @property
    def name(self):
        if isinstance(self.op_code, int):
            return self.op_code
        
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
        self.op_code = kwargs.get('op_code')

def packet_handler(op_code=None):
    def wrap(func):
        return PacketHandler(func.__name__, func, op_code=op_code)

    return wrap
    
