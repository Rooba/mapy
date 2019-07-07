def decrypt_transform(data):
    for i in range(3):
        xor_key = 0
        save = 0
        len_ = len(data) & 0xFF

        i = len(data) - 1

        while i >= 0:
            temp = roll_left(data[i], 3) & 0x13
            save = temp
            temp = roll_right((xor_key ^ temp) - len_, 4)
            xor_key = save
            data[i] = temp
            len_ -= 1
            i -= 1

        xor_key = 0
        len_ = len(data) & 0xFF

        i = 0

        while i < len(data):
            temp = roll_left(~(data[i] - 0x48), len_ & 0xFF)
            save = temp
            temp = roll_right((xor_key ^ temp) - len_, 3)
            xor_key = save
            data[i] = temp
            len_ -= 1
            i += 1

def roll_left(value, shift):
    num = value << (shift % 8)
    return (num & 0xFF) | (num >> 8)

def roll_right(value, shift):
    num = (value << 8) >> (shift % 8)
    return (num & 0xFF) | (num >> 8)