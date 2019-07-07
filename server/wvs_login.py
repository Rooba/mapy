import asyncio
import logging

log = logging.getLogger(__name__)

from common.constants import LOGIN_PORT, CENTER_PORT, HOST_IP, AUTO_REGISDTER, MAX_CHARACTERS,\
                            REQUEST_PIC, REQUEST_PIN, REQUIRE_STAFF_IP, WORLD_COUNT

from common.enum import ServerRegistrationResponse

from net.packets.opcodes import CRecvOps, InterOps
from net.packets import crypto, Packet
from net.packets.packet import packet_handler
from utils.cpacket import COutPacket

from server._wvs_login import Channel, World, CenterServer
from server.server_base import ServerBase

class WvsLogin(ServerBase):
    __opcodes__ = CRecvOps
    __crypto__ = crypto.MapleCryptograph

    # TODO: Connect to center and store under self.__parent

    def __init__(self, loop=None, security_key=None):
        loop = loop if loop is not None else asyncio.get_event_loop()

        super().__init__(LOGIN_PORT, 'LoginServer', loop)
        self._security_key = security_key
        self._clients = []
        self._worlds = []
        self._auto_register = AUTO_REGISDTER
        self._request_pin = REQUEST_PIN
        self._request_PIC = REQUEST_PIC
        self._require_staff_ip = REQUIRE_STAFF_IP
        self._max_characters = MAX_CHARACTERS

        for i in range(WORLD_COUNT):
            self._worlds.append(World(i))

        self._center = CenterServer(self, HOST_IP, CENTER_PORT)

    ##
    # InterOps 
    ##

    @packet_handler(InterOps.RegistrationResponse)
    async def registration_response(self, client, packet):
        response = ServerRegistrationResponse(packet.decode_byte())
        
        if response == ServerRegistrationResponse.Valid:
            self._loop.create_task(self.listen())

            log.debug("Registered Login Server")
        
        else:
            log.error("Failed to register Login Server [Reason: %s]", response.name)

            self.is_alive = False
    
    @packet_handler(InterOps.UpdateChannel)
    async def update_channel(self, client, packet):
        pass

    @packet_handler(InterOps.UpdateChannelPopulation)
    async def update_channel_population(self, client, packet):
        pass

    @packet_handler(InterOps.CharacterNameCheckResponse)
    async def check_character_name(self, client, packet):
        pass
    
    @packet_handler(InterOps.CharacterEntriesResponse)
    async def get_characters(self, client, packet):
        pass

    @packet_handler(InterOps.CharacterCreationResponse)
    async def create_character(self, client, packet):
        pass

    @packet_handler(InterOps.MigrationRegisterResponse)
    async def migrate(self, client, packet):
        pass

    ##
    # End InterOps
    ##

    @packet_handler(CRecvOps.CheckPassword)
    async def try_login(self, client, packet):
        password = packet.decode_string()
        username = packet.decode_string().lower()
        
        response = await client.login(username, password)

        await client.send_packet(COutPacket.check_password_result(client, response))