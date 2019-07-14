from server.server_base import ServerBase
from server._wvs_login import Channel, World, CenterServer
from utils.cpacket import CPacket
from net.packets.packet import packet_handler
from net.packets import Packet
from net.packets.opcodes import CRecvOps, InterOps, CSendOps
from client.entities import Account
from client import WvsLoginClient
from common.enum import ServerRegistrationResponse
from common.constants import LOGIN_PORT, CENTER_PORT, HOST_IP, AUTO_REGISDTER, MAX_CHARACTERS,\
    REQUEST_PIC, REQUEST_PIN, REQUIRE_STAFF_IP, WORLD_COUNT, AUTO_LOGIN, CENTER_KEY
import asyncio
import logging

log = logging.getLogger(__name__)


class WvsLogin(ServerBase):
    __opcodes__ = CRecvOps

    def __init__(self, loop=None):

        super().__init__('LoginServer')

        self._center = CenterServer

        self._security_key = CENTER_KEY
        self._worlds = []
        self._auto_register = AUTO_REGISDTER
        self._request_pin = REQUEST_PIN
        self._request_PIC = REQUEST_PIC
        self._require_staff_ip = REQUIRE_STAFF_IP
        self._max_characters = MAX_CHARACTERS
        self._login_pool = []

        # for i in range(WORLD_COUNT):
        #     self._worlds.append(World(i + 1))
        self._worlds.append(World(15))

    def run(self):
        super().run(LOGIN_PORT)

    ##
    # InterOps
    ##

    @packet_handler(InterOps.RegistrationResponse)
    async def registration_response(self, client, packet):
        response = ServerRegistrationResponse(packet.decode_byte())

        if response == ServerRegistrationResponse.Valid:
            self._loop.create_task(self.listen())

            log.info("Registered Login Server")

        else:
            log.error(
                "Failed to register Login Server [Reason: %s]", response.name)

            self.is_alive = False

    @packet_handler(InterOps.UpdateChannel)
    async def update_channel(self, client, packet):
        world_id = packet.decode_byte()
        add = packet.decode_bool()
        world = self._worlds[world_id]

        if add:
            world._channels.append(Channel(packet))

        else:
            channel_id = packet.decode_byte()
            world._channels.pop(channel_id)

    @packet_handler(InterOps.UpdateChannelPopulation)
    async def update_channel_population(self, client, packet):
        world_id = packet.decode_byte()
        channel_id = packet.decode_byte()

        self._worlds[world_id]._channels[channel_id].population = packet.decode_int()

    @packet_handler(InterOps.CharacterNameCheckResponse)
    async def check_character_name(self, client, packet):
        # Don't need this?
        pass

    async def is_name_taken(self, name):
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

    async def client_connect(self, client):
        return WvsLoginClient(self, client)

    @packet_handler(CRecvOps.CP_CreateSecurityHandle)
    async def create_secuirty_heandle(self, client, packet):
        if AUTO_LOGIN:
            i_packet = Packet(op_code=CRecvOps.CP_CheckPassword)
            i_packet.encode_string("admin")
            i_packet.encode_string("admin")
            i_packet.seek(2)
            client.dispatch(i_packet)

    @packet_handler(CRecvOps.CP_CheckDuplicatedID)
    async def check_duplicated_id(self, client, packet):
        username = packet.decode_string()
        is_available = await self._api.is_username_taken(username)

        await client.send_packet(CPacket.check_duplicated_id_result(username, is_available))

    async def login(self, client, username, password):
        client.account = Account(id=2001, username=username, password=password)
        # client.set_account(data)

        return 0

    @packet_handler(CRecvOps.CP_CheckPassword)
    async def check_password(self, client, packet):

        password = packet.decode_string()
        username = packet.decode_string()

        response = await client.login(username, password)

        await client.send_packet(CPacket.check_password_result(client, response))

    @packet_handler(CRecvOps.CP_WorldRequest)
    async def world_request(self, client, packet):
        for world in self._worlds:
            await client.send_packet(CPacket.world_information(world))

        await client.send_packet(CPacket.end_world_information())
        await client.send_packet(CPacket.latest_connected_world(self._worlds[0]))

    @packet_handler(CRecvOps.CP_CheckUserLimit)
    async def check_user_limit(self, client, packet):
        world = packet.decode_short()
        await client.send_packet(CPacket.check_user_limit(0))

    @packet_handler(CRecvOps.CP_SelectWorld)
    async def select_world(self, client, packet):
        packet.decode_byte()

        world_id = packet.decode_byte()
        channel_id = packet.decode_byte()
        
        await client.load_avatars() # Load avatars for specific world in future
        
        await client.send_packet(CPacket.world_result(client.avatars))
