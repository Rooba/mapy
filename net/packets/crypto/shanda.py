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
    for _ in range(3):
        xor_key = 0
        length = len(data) & 0xFF

        i = 0

        for i in range(len(data)):
            cur = (((roll_left(data[0], 3)) + length) ^ xor_key)
            xor_key = cur
            cur = (((~roll_right(cur, length & 0xFF)) & 0xFF) + 0x48)
            data[i] = cur 
            length -= 1
        
        xor_key = 0
        length = len(data) & 0xFF

        i = len(data) - 1

        while i >= 0:
            cur = (xor_key ^ (length + (roll_left(data[i], 4))))
            xor_key = cur
            cur = roll_right(cur ^ 0x13, 3)
            data[i] = cur
            length -= 1
            i -= 1

    return data


def roll_left(inn, count):
    tmp = inn & 0xFF
    tmp = tmp << (count % 8)
    return ((tmp & 0xFF) | (tmp >> 8))


def roll_right(inn, count):
    tmp = inn & 0xFF
    tmp = (tmp << 8) >> (count % 8)
    return (tmp & 0xFF) | (tmp >> 8)