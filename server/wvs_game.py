import asyncio
from loguru import logger

from common.constants import CENTER_PORT, HOST_IP
from common.enum import ServerRegistrationResponse
from net.packets.opcodes import CRecvOps, InterOps
from net.packets import crypto, Packet
from net.packets.packet import packet_handler
from .server_base import ServerBase
from ._wvs_game.center_server import CenterServer

class WvsGame(ServerBase):

    __opcodes__ = CRecvOps

    def __init__(self, loop=None, security_key=None):
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._port = None

        super().__init__(self._port, 'GameServer', self._loop)

        self._ready = asyncio.Event(loop = self._loop)
        self._world_id = None
        self._world_name = ""
        self._ticker_message = ""
        self._channel_id = None
        self._allow_multi_leveling = False
        self._exp_rate = 1
        self._quest_exp_rate = 1
        self._party_quest_exp_rate = 1
        self._meso_rate = 1
        self._drop_rate = 1

        self._packet_handlers = []
        self._security_key = security_key
        self.add_packet_handlers()

        self._center = CenterServer(self, HOST_IP, CENTER_PORT)

    @packet_handler(InterOps.RegistrationResponse)
    async def registration_response(self, client, packet):
        response = ServerRegistrationResponse(packet.decode_byte())

        if response == ServerRegistrationResponse.Valid:
            self.world_id = packet.decode_byte()
            self.world_name = packet.decode_string()
            self.ticker_message = packet.decode_string()
            self.channel_id = packet.decode_byte()
            self._port = packet.decode_short()
            self.allow_multi_leveling = packet.decode_bool()
            self.exp_rate = packet.decode_int()
            self.quest_exp_rate = packet.decode_int()
            self.party_quest_exp_rate = packet.decode_int()
            self.meso_rate = packet.decode_int()
            self.drop_rate = packet.decode_int()

            logger.info("Registered Game Server [World Name: {}] [World ID: {}] [Channel ID: {}]", 
                self.world_name, self.world_id, self.channel_id)

            self.start_acceptor(self._port)
            self._loop.create_task(self.listen())

        else:
            logger.error("Unable to register Game Server [Reason: {}]", response.name)

            self.is_alive = False

    @property
    def world_id(self):
        return self._world_id
    
    @world_id.setter
    def world_id(self, value):
        self._world_id = value

    @property
    def world_name(self):
        return self._world_name

    @world_name.setter
    def world_name(self, value):
        self._world_name = value
    
    @property
    def ticker_message(self):
        return self._ticker_message
    
    @ticker_message.setter
    def ticker_message(self, value):
        self._ticker_message = value

    @property
    def channel_id(self):
        return self._channel_id

    @channel_id.setter
    def channel_id(self, value):
        self._channel_id = value

    @property
    def allow_multi_leveling(self):
        return self._allow_multi_leveling

    @allow_multi_leveling.setter
    def allow_multi_leveling(self, value):
        self._allow_multi_leveling = value

    @property
    def exp_rate(self):
        return self._exp_rate

    @exp_rate.setter
    def exp_rate(self, value):
        self._exp_rate = value

    @property
    def quest_exp_rate(self):
        return self._quest_exp_rate

    @quest_exp_rate.setter
    def quest_exp_rate(self, value):
        self._quest_exp_rate = value

    @property
    def party_quest_exp_rate(self):
        return self._party_quest_exp_rate

    @party_quest_exp_rate.setter
    def party_quest_exp_rate(self, value):
        self._party_quest_exp_rate = value

    @property
    def meso_rate(self):
        return self._meso_rate

    @meso_rate.setter
    def meso_rate(self, value):
        self._meso_rate = value
    
    @property
    def drop_rate(self):
        return self._drop_rate

    @drop_rate.setter
    def drop_rate(self, value):
        self._drop_rate = value
            