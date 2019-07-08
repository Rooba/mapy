from .aes import MapleAes
from .shanda import decrypt_transform

class BlankCryptograph:
    pass

class MapleCryptograph(BlankCryptograph):
    
    @classmethod
    def transform(cls, buffer, iv):
        maes = MapleAes()

        buf = buffer[4:]
        maes.transform(buf, iv)
        decrypt_transform(buf)

        return buf

        
            