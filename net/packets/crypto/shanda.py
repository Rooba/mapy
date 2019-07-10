def decrypt_transform(data):
    for j in range(1, 7):
        remember = 0
        data_length = len(data) & 0xFF
        next_remember = 0
        if j % 2 == 0:
            for i in range(len(data)):
                cur = data[i]
                cur -= 0x48
                cur = ~cur & 0xFF
                cur = roll_left(cur, data_length & 0xFF)
                next_remember = cur
                cur ^= remember
                remember = next_remember
                cur -= data_length
                cur = roll_right(cur, 3)
                data[i] = cur
                data_length -= 1
        else:
            for i in reversed(range(len(data))):
                cur = data[i]
                cur = roll_left(cur, 3)
                cur ^= 0x13
                next_remember = cur
                cur ^= remember
                remember = next_remember
                cur -= data_length
                cur = roll_right(cur, 4)
                data[i] = cur
                data_length -= 1

    return data

def encrypt_transform(data):
    ## DOES NOT WORK
    b = {str(i): 0 for i in range(len(data))}
    cur = 0

    for _ in range(3):
        length = len(data) & 0xFF
        xor_key = 0
        i = 0
        while i < len(data):
            
            cur = roll_left(data[i], 3)
            cur = cur + length
            cur = (cur ^ xor_key) & 0xFF
            xor_key = cur
            cur = ~roll_right(cur, length & 0xFF) & 0xFF
            cur = (cur + 0x48) & 0xFF
            data[i] = cur
            b[str(i)] = cur
            length -= 1
            i += 1


        xor_key = 0
        length = len(data) & 0xFF
        i = len(data) - 1

        while i >= 0:
            cur = roll_left(data[i], 4)
            cur += length
            cur = (cur ^ xor_key) & 0xFF
            xor_key = cur
            cur ^= 0x13
            cur = roll_right(cur, 3)
            data[i] = cur
            b[str(i)] = cur
            length -= 1
            i -= 1

    return bytearray([b[b_] for b_ in b])


def roll_left(value, shift):
    num = value << (shift % 8)
    return ((num & 0xFF) | (num >> 8))

def roll_right(value, shift):
    num = (value << 8) >> (shift % 8)
    return ((num & 0xFF) | (num >> 8))