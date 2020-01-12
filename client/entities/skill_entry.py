from dataclasses import dataclass, field

from common.abc import WildcardData
from common.constants import PERMANENT

@dataclass
class SkillEntry(WildcardData):
    id: int             = 0
    level: int          = 0
    mastery_level: int  = 0
    max_level: int      = 0
    expiration: int     = field(default=PERMANENT)

    def encode(self, packet):
        packet.encode_int(self.id)
        packet.encode_int(self.level)
        packet.encode_long(PERMANENT) # skill.expiration