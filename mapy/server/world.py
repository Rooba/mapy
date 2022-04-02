from mapy import constants
from mapy.common.enum import WorldFlag, Worlds


class World:

    def __init__(self, id):
        self._world = Worlds(id)
        self._channels = []
        self._flag = WorldFlag.New
        self._allow_multi_leveling = constants.ALLOW_MULTI_LEVELING
        self._default_creation_slots = constants.DEFAULT_CREATION_SLOTS
        self._disable_character_creation = False
        self.event_message = constants.DEFAULT_EVENT_MESSAGE
        self.ticker_message = constants.DEFAULT_TICKER
        self.exp_rate = constants.EXP_RATE
        self.quest_exp_rate = constants.QUEST_EXP
        self.party_quest_exp_rate = constants.PARTY_QUEST_EXP
        self.meso_rate = constants.MESO_RATE
        self.drop_rate = constants.DROP_RATE

    @property
    def id(self):
        return self._world.value

    @property
    def name(self):
        return self._world.name

    @property
    def port(self):
        return 8585 + (20 * self._world.value)

    @property
    def population(self):
        return sum([channel.population for channel in self._channels])

    @property
    def channels(self):
        return self._channels

    def add_channel(self, item):
        self._channels.append(item)

    def __getitem__(self, key):
        for channel in self._channels:
            if channel.channel_id == key:
                return channel

        return None
