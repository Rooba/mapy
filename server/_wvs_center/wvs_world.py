from common.constants import CHANNEL_COUNT
from . import ChannelManager

class WvsWorld:
    def __init__(self, parent, id=None, name=None, port=None, channels=None,
                ticker_message="Default Message", allow_multi_leveling=False, exp_rate=1,
                quest_exp=1, party_exp=1, meso_rate=1, drop_rate=1):
                
        self._id = id
        self._name = name
        self._port = port
        self._channel_count = channels
        self._channels = ChannelManager(self, self._channel_count)
        self._ticker_message = ticker_message
        self._allow_multi_leveling = allow_multi_leveling
        self._exp_rate = exp_rate
        self._quest_exp = quest_exp
        self._party_exp = party_exp
        self._meso_rate = meso_rate
        self._drop_rate = drop_rate
    
    @classmethod
    def from_packet(cls, parent, packet):
        world = {
            'id': packet.decode_byte(),
            'name': packet.decode_string(),
            'port': packet.decode_short(),
            'channels': packet.decode_byte(),
            'ticker_message': packet.decode_string(),
            'allow_multi_leveling': bool(packet.decode_byte()),
            'exp_rate': packet.decode_int(),
            'quest_exp': packet.decode_int(),
            'party_exp': packet.decode_int(),
            'meso_rate': packet.decode_int(),
            'drop_rate': packet.decode_int(),
        }

        return WvsWorld(parent, **world)

    @property
    def id(self):
        return self._id

    @property
    def channels(self):
        return self._channels