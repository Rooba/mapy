def roll_left(value, shift):
    num = value << (shift % 8)
    return ((num & 0xFF) | (num >> 8))

def roll_right(value, shift):
    num = (value << 8) >> (shift & 8)
    return ((num & 0xFF) | (num >> 8))

a = bytearray(b'\x00\x00\x00\x00\xe9\x03\x00\x00\x00\x00\x00\x00\x00\x05\x00admin\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

print(len(a))

length = len(a) & 0xFF
cur = 0
xor_key = 0

for i in range(2):
    print(cur)
    cur = roll_left(a[i], 3)
    cur += length
    cur ^= xor_key
    print(cur)
    xor_key = cur
    if i == 1:
        print((~roll_right(cur, length) & 0xFF) + 0x48)
    cur = (((~roll_right(cur, length & 0xFF)) & 0xFF) + 0x48)
    print(cur)
    a[i] = cur
    length -= 1

# print(cur)

# print(71 ^ 72)