from Cryptodome.Cipher import AES

class MapleAes:
    _user_key = bytearray([
        0x13, 0x00, 0x00, 0x00,
        0x08, 0x00, 0x00, 0x00,
        0x06, 0x00, 0x00, 0x00,
        0xb4, 0x00, 0x00, 0x00,
        0x1b, 0x00, 0x00, 0x00,
        0x0f, 0x00, 0x00, 0x00,
        0x33, 0x00, 0x00, 0x00,
        0x52, 0x00, 0x00, 0x00
    ])

    @classmethod
    def transform(cls, buffer, iv):
        remaining = len(buffer)
        length = 0x5B0
        start = 0

        real_iv = bytearray(16)

        iv_bytes = [
            iv.value & 255,
            iv.value >> 8 & 255,
            iv.value >> 16 & 255,
            iv.value >> 24 & 255,
        ]

        while remaining > 0:
            for index in range(len(real_iv)):
                real_iv[index] = iv_bytes[index % 4]
            
            if remaining < length:
                length = remaining

            index = start

            while index < start + length:
                sub = index - start

                if (sub % 16) == 0:
                    real_iv = AES.new(cls._user_key, AES.MODE_ECB).encrypt(real_iv)

                buffer[index] ^= real_iv[sub % 16]
                index += 1
            
            start += length
            remaining -= length
            length = 0x5B4

        iv.shuffle()

        return buffer
    
    @staticmethod
    def get_header(data, iv, length, major_ver):
            first = -(major_ver + 1) ^ iv.hiword
            a = first & 0xFF
            b = first >> 8 & 0xFF
            second = (a & 0xFF | b << 8 & 0xFF00) ^ length
            c = second & 0xFF
            d = second >> 8 & 0xFF
            data[0:4] = bytearray([a, b, c, d])
            return data