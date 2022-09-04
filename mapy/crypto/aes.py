try:
    from Cryptodome.Cipher import AES  # type: ignore
except ImportError:
    from Crypto.Cipher import AES  # type: ignore
except ImportError:
    raise Exception("Please install pycryptodomex")

# from struct import unpack, pack


class MapleAes:
    _user_key = bytearray([
        0x13, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00,
        0xB4, 0x00, 0x00, 0x00, 0x1B, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x00, 0x00,
        0x33, 0x00, 0x00, 0x00, 0x52, 0x00, 0x00, 0x00
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
                    real_iv = AES.new(cls._user_key,
                                      AES.MODE_ECB).encrypt(real_iv)

                buffer[index] ^= real_iv[sub % 16]
                index += 1

            start += length
            remaining -= length
            length = 0x5B4

        iv.shuffle()

        return buffer

    # @staticmethod
    # def get_header(data, iv, length, major_ver):
    #     first = -(major_ver + 1) ^ iv.hiword
    #     a = first & 0xFF
    #     b = first >> 8 & 0xFF
    #     second = (a & 0xFF | b << 8 & 0xFF00) ^ length
    #     c = second & 0xFF
    #     d = second >> 8 & 0xFF
    #     data[0:4] = bytearray([a, b, c, d])
    #     return data

    @staticmethod
    def get_header(data, iv, length, major_ver):
        first = -(major_ver + 1) ^ iv.hiword
        second = (first + 2**16) ^ length
        data[0:2] = bytes([first & 0xFF, first >> 8 & 0xFF])
        data[2:4] = bytes([second & 0xFF, second >> 8 & 0xFF])

    @staticmethod
    def get_length(data):
        return ((data[1] << 8) + data[0]) ^ ((data[3] << 8) + data[2])
