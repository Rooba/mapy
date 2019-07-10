from pyaes import AESModeOfOperationCBC
import struct

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
        from Cryptodome.Cipher import AES
        
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
            data[0:2] = (-(major_ver + 1) ^ iv.hiword).to_bytes(2, 'little', signed = True)
            data[2:4] = (first ^ length).to_bytes(2, 'little', signed = True)
            return data