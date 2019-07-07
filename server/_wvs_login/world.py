from common import constants
from common.enum import WorldFlag

class World:
    def __init__(self, id):
        self._id = id
        self._name = "Kastia"
        self._port = 8585 + 100 * self._id
        self._shop_port = 9000
        self._channels = []
        self._flag = WorldFlag.New
        self._event_message = constants.DEFAULT_EVENT_MESSAGE
        self._ticker_message = constants.DEFAULT_TICKER
        self._allow_multi_leveling = constants.ALLOW_MULTI_LEVELING
        self._default_creation_slots = constants.DEFAULT_CREATION_SLOTS
        self._disable_character_creation = False
        self._exp_rate = constants.EXP_RATE
        self._quest_exp_rate = constants.QUEST_EXP
        self._party_quest_exp_rate = constants.PARTY_QUEST_EXP
        self._meso_rate = constants.MESO_RATE
        self._drop_rate = constants.DROP_RATE

    def add_channel(self, item):
        self._channels.append(item)
    
    @property
    def population(self):
        return sum([channel.population for channel in self._channels])