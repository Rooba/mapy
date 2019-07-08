def decrypt_transform(data):
    # size = len(data)

    # for i in range(3):
    #     a = 0
    #     b = 0
        
    #     j = size
    #     while j > 0:
    #         c = data[j - 1]
    #         c = roll_left(c, 3)
    #         c ^= 0x13
    #         a = c
    #         c ^= b
    #         c = (c - j)
    #         c = roll_right(c, 4)
    #         b = a
    #         data[j - 1] = c

    #         j -= 1

    #     a = 0
    #     b = 0

    #     j = size
    #     while j > 0:
    #         c = data[size - 1]
    #         c -= 0x48
    #         c ^= 0xFF
    #         c = roll_left(c, j)
    #         a = c
    #         c ^= b
    #         c = (c - j)
    #         c = roll_right(c, 3)
    #         b = a
    #         data[size - j] = c
    #         j -= 1

    #     return data


    # for j in range(1, 7):
    #     remember = 0
    #     data_length = len(data) & 0xFF
    #     next_remember = 0
    #     if j % 2 == 0:
    #         for i in range(len(data)):
    #             cur = data[i]
    #             cur -= 0x48
    #             cur = ~cur & 0xFF
    #             cur = roll_left(cur, data_length & 0xFF)
    #             next_remember = cur
    #             cur ^= remember
    #             remember = next_remember
    #             cur -= data_length
    #             cur = roll_right(cur, 3)
    #             data[i] = cur
    #             data_length -= 1
    #     else:
    #         for i in reversed(range(len(data))):
    #             cur = data[i]
    #             cur = roll_left(cur, 3)
    #             cur ^= 0x13
    #             next_remember = cur
    #             cur ^= remember
    #             remember = next_remember
    #             cur -= data_length
    #             cur = roll_right(cur, 4)
    #             data[i] = cur
    #             data_length -= 1


                
    for _ in range(3):
        xor_key = 0
        save = 0
        len_ = len(data) & 0xFF
        
        print(len(data), len(data) & 0xFF)

        i = len(data) - 1

        while i >= 0:
            temp = roll_left(data[i], 3) ^ 0x13
            save = temp
            temp = roll_right(((xor_key ^ temp) - len_), 4)
            xor_key = save
            data[i] = temp
            len_ -= 1
            i -= 1

        xor_key = 0
        len_ = len(data) & 0xFF

        i = 0

        while i < len(data):
            temp = roll_left((~(data[i] - 0x48)), len_ & 0xFF)
            save = temp
            temp = roll_right(((xor_key ^ temp) - len_), 3)
            xor_key = save
            data[i] = temp
            len_ -= 1
            i += 1

    return data

def encrypt_transform(data):
    for _ in range(3):
        xor_key = 0
        length = len(data) & 0xFF

        for i in range(len(data)):
            cur = (roll_left(data[i], 3) + length) ^ xor_key
            xor_key = cur

            cur = ((~roll_right(cur, length & 0xFF)) & 0xFF) + 0x48
            data[i] = cur
            length -= 1
        
        xor_key = 0
        length = len(data) & 0xFF

        i = len(data) - 1

        while i >= 0:
            cur = (xor_key ^ (length + roll_left(data[i], 4)))
            xor_key = cur
            cur = roll_right((cur ^ 0x13), 3)
            data[i] = cur
            length -= 1
            i -= 1
    
    return data


def roll_left(value, shift):
    tmp = value & 0xFF
    tmp = tmp << (shift % 8)
    return ((tmp & 0xFF) | (tmp >> 8))

def roll_right(value, shift):
    tmp = value & 0xFF
    tmp = (tmp << 8) >> (shift % 8)
    return (tmp & 0xFF) | (tmp >> 8)