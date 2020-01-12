from random import randint

class Random:
    def __init__(self):
        self.seed_1 = randint(1, 2**31-1)
        self.seed_2 = randint(1, 2**31-1)
        self.seed_3 = randint(1, 2**31-1)

    def encode(self, packet):
        packet.encode_int(self.seed_1)
        packet.encode_int(self.seed_2)
        packet.encode_int(self.seed_3)