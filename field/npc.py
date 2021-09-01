from dataclasses import dataclass

from .life import Life
from .move_path import MovePath


@dataclass
class Npc(Life):
    def __post_init__(self):
        self.pos = MovePath(self.x, self.cy, self.foothold)
        self.id = self.life_id