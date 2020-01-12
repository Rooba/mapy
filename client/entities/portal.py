from dataclasses import dataclass

from common.abc import WildcardData
from utils import TagPoint


@dataclass
class Portal(WildcardData):
    id: int                 = 0
    name: str               = ""
    type: int               = 0
    destination: int        = 0
    destination_label: str  = ""
    x: int              = 0
    y: int              = 0

    def __post_init__(self):
        self.point = TagPoint(self.x, self.y)
    
    def __str__(self):
        return f"{id} @ {self.point} -> {self.destination}"