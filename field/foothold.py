from dataclasses import dataclass

from common.abc import WildcardData


@dataclass
class Foothold(WildcardData):
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
