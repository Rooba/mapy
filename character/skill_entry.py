from dataclasses import dataclass, field
from typing import List

from common.abc import WildcardData
from common.constants import PERMANENT

def default_level_data():
    return []

@dataclass
class SkillEntry(WildcardData):
    id: int             = 0
    level: int          = 0
    mastery_level: int  = 0
    max_level: int      = 0
    expiration: int     = field(default=PERMANENT)
    level_data: List    = field(default_factory=default_level_data)

    def encode(self, packet):
        packet.encode_int(self.id)
        packet.encode_int(self.level)
        packet.encode_long(PERMANENT) # skill.expiration