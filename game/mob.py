from dataclasses import dataclass 

from .life import Life
from utils import MapPos

@dataclass
class Mob(Life):
    mob_id: int = 0
    hp: int     = 0
    mp: int     = 0
    
    hp_recovery: int    = 0
    mp_recovery: int    = 0
    exp: int            = 0

    physical_attack: int = 0

    def __post_init__(self):
        self.attackers = {}
        self.pos = MapPos(self.x, self.cy, self.foothold)
        self.cur_hp = self.hp
        self.cur_mp = self.mp
        self.controller = 0

    @property
    def dead(self):
        return self.cur_hp <= 0

    def damage(self, character, amount):
        pass

    def encode_init(self, packet):
        packet.encode_int(self.obj_id)
        packet.encode_byte(5)
        packet.encode_int(self.life_id)

        # Set Temporary Stat
        packet.encode_long(0)
        packet.encode_long(0)

        packet.encode_short(self.pos.position.x)
        packet.encode_short(self.pos.position.y)
        packet.encode_byte(0 & 1 | 2 * 2)
        packet.encode_short(self.pos.foothold)
        packet.encode_short(self.pos.foothold)

        packet.encode_byte(abs(-2))

        packet.encode_byte(0)
        packet.encode_int(0)
        packet.encode_int(0)