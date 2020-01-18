from dataclasses import dataclass

from .life import Life
from utils import MapPos


@dataclass
class Npc(Life):
    def __post_init__(self):
        self.pos = MapPos(self.x, self.cy, self.foothold)
        self.id = self.life_id