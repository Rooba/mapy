from attrs import define, field

from ..common.constants import PERMANENT


@define(kw_only=True)
class SkillEntry(object):
    id: int = int()
    level: int = int()
    mastery_level: int = int()
    max_level: int = int()
    expiration: int = PERMANENT
    level_data: list = field(factory=lambda: list())

    def encode(self, packet):
        packet.encode_int(self.id)
        packet.encode_int(self.level)
        packet.encode_long(PERMANENT)  # skill.expiration
