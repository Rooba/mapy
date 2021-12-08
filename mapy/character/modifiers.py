from mapy.common import StatModifiers
from mapy.common.constants import is_extend_sp_job
from mapy.utils.cpacket import CPacket


class StatModifier:
    def __init__(self, character_stats):
        self._modifiers = []
        self._stats = character_stats

    @property
    def modifiers(self):
        return self._modifiers

    @property
    def flag(self):
        _flag = 0
        for mod in self._modifiers:
            _flag |= mod.value
        return _flag

    def alter(self, **stats):
        for key, val in stats.items():
            modifier = StatModifiers[key.upper()]
            self._modifiers.append(modifier)
            setattr(self._stats, key, val)

    def encode(self, packet):
        packet.encode_int(self.flag)

        for modifier in StatModifiers:
            if modifier not in self._modifiers:
                continue

            if modifier is StatModifiers.SP:
                if is_extend_sp_job(self._stats.job):
                    packet.encode_byte(0)
                else:
                    packet.encode_short(self._stats.sp)
            else:
                getattr(packet, f"encode_{modifier.encode}")(
                    packet, getattr(self._stats, modifier.name.lower())
                )


class CharacterModifiers:
    def __init__(self, character):
        self._parent = character

    async def stats(self, *, excl_req=True, **stats):
        modifier = StatModifier(self._parent.stats)
        modifier.alter(**stats)

        if modifier.modifiers:
            await self._parent.send_packet(CPacket.stat_changed(modifier, excl_req))
