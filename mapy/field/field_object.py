from attrs import define, field

from ..tools import TagPoint
from .field import Field
from .move_path import MovePath


@define
class FieldObject(object):
    _obj_id: int = -1
    _position: MovePath = MovePath()
    _field: Field | None = None


@define
class Foothold(object):
    id: int = 0
    prev: int = 0
    next: int = 0
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0

    @property
    def wall(self):
        return self.x1 == self.x2

    def compare_to(self, foothold):
        if self.y2 < foothold.y1:
            return -1
        if self.y1 > foothold.y2:
            return 1
        return 0


@define
class Portal(object):
    _id: int = field(default=0)
    name: str = ""
    _type: int = field(default=0)
    destination: int = 0
    destination_label: str = ""
    x: int = 0
    y: int = 0

    def __post_init__(self):
        self.point = TagPoint(self.x, self.y)

    def __str__(self):
        return f"{id} @ {self.point} -> {self.destination}"


@define
class Life(FieldObject):
    life_id: int = 0
    life_type: str = ""
    foothold: int = 0
    x: int = 0
    y: int = 0
    cy: int = 0
    f: int = 0
    hide: int = 0
    rx0: int = 0  # min click position
    rx1: int = 0  # max click position
    mob_time: int = 0


@define
class Mob(Life):
    mob_id: int = 0
    hp: int = 0
    mp: int = 0
    hp_recovery: int = 0
    mp_recovery: int = 0
    exp: int = 0
    physical_attack: int = 0

    def __post_init__(self):
        self.attackers = {}
        self.pos = MovePath(self.x, self.cy, self.foothold)
        self.cur_hp = self.hp
        self.cur_mp = self.mp
        self.controller = 0

    @property
    def dead(self):
        return self.cur_hp <= 0

    def damage(self, character, amount):
        pass

    def encode_init(self, packet):
        packet.encode_int(self._obj_id)
        packet.encode_byte(5)
        packet.encode_int(self.life_id)

        # Set Temporary Stat
        packet.encode_long(0)
        packet.encode_long(0)

        packet.encode_short(self.pos.x)
        packet.encode_short(self.pos.y)
        packet.encode_byte(0 & 1 | 2 * 2)
        packet.encode_short(self.pos.foothold)
        packet.encode_short(self.pos.foothold)

        packet.encode_byte(abs(-2))

        packet.encode_byte(0)
        packet.encode_int(0)
        packet.encode_int(0)


@define
class Npc(Life):
    def __post_init__(self):
        self.pos = MovePath(self.x, self.cy, self.foothold)
        self.id = self.life_id
