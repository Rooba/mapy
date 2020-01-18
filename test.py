from struct import pack
from timeit import timeit

def use_struct():
    pack('H', 65535)

def use_bitwise():
    bytes([65535 >> 8, 65535 & 0xFF])

print(timeit(use_struct, number=100000))
print(timeit(use_bitwise, number=100000))