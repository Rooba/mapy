from common.constants import CHANNEL_COUNT
from . import WvsGameManager

class World:
    def __init__(self, id=None, name=None, channels=None, channel_limit=None,
                ticker_message="Default Message", allow_multi_leveling=False, exp_rate=1,
                quest_exp=1, party_exp=1, meso_rate=1, drop_rate=1):
                
        self._id = id
        self.name = name
        self._channels = WvsGameManager(self)
        self.channel_limit = channel_limit
        self.ticker_message = ticker_message
        self.allow_multi_leveling = allow_multi_leveling
        self.exp_rate = exp_rate
        self.quest_exp = quest_exp
        self.party_exp = party_exp
        self.meso_rate = meso_rate
        self.drop_rate = drop_rate
    
    def from_packet(self, packet):
        self.name = packet.decode_string()
        self.channel_limit = packet.decode_byte()
        self.ticker_message = packet.decode_string()
        self.allow_multi_leveling = packet.decode_bool()
        self.exp_rate = packet.decode_int()
        self.quest_exp = packet.decode_int()
        self.party_exp = packet.decode_int()
        self.meso_rate = packet.decode_int()
        self.drop_rate = packet.decode_int()

        return self

    @property
    def id(self):
        return self._id

    @property
    def channels(self):
        return self._channels

    @property
    def channel_count(self):
        return len(self._channels)