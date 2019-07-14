from server._wvs_center import World, WorldManager
from server import ServerBase
from net.packets.opcodes import InterOps
from net.packets.packet import packet_handler, Packet
from client import WvsCenterClient
from common.enum import ServerType, ServerRegistrationResponse
from common import constants
import logging

log = logging.getLogger(__name__)


class CenterServer(ServerBase):
    """Server connection listener for incoming client socket connections

    Attributes
    -----------
    is_alive: :class:`bool`
        Server alive status
    name: :class:`str`
        Server specific name
    _login: :class:`LoginServer`
        Registered :class:`Login` Server
    _worlds: :class:`Worlds`[:class:`World`]
        List of registered :class:`World` clients
    shop: :class:`ShopServer`
        Connected `ShopServer`

    """

    __opcodes__ = InterOps

    def __init__(self, loop=None):
        super().__init__('CenterServer')
        self._security_key = constants.CENTER_KEY
        self._login = None
        self._worlds = WorldManager(self, constants.WORLD_COUNT)
        self._shop = None

    async def client_connect(self, client):
        return WvsCenterClient(self, client)

    async def on_client_disconnect(self, client):
        if client == self._login:
            self._login = None

            # for world in self._worlds:
            # for channel in world.channels:
            # Tell WvsGame that login server went down
            # pass

        await super().on_client_disconnect(client)

    def run(self):
        super().run(constants.CENTER_PORT, True)

    @packet_handler(InterOps.RegistrationRequest)
    async def registration_request(self, client, packet):
        server_type = packet.decode_byte()
        security_key = packet.decode_string()

        with Packet(op_code=InterOps.RegistrationResponse) as out_packet:
            try:
                server_type = ServerType(server_type)
            except ValueError:
                out_packet.encode_byte(ServerRegistrationResponse.InvalidType)
                return await client.send_packet_raw(out_packet)

            if security_key != self._security_key:
                out_packet.encode_byte(ServerRegistrationResponse.InvalidCode)
                return await client.send_packet_raw(out_packet)

            valid_world = self._worlds.get_open()

            if server_type == ServerType.login and self._login or \
                    server_type == ServerType.channel and not valid_world or \
                    server_type == ServerType.shop and self._shop:
                out_packet.encode_byte(ServerRegistrationResponse.Full)
                return await client.send_packet_raw(out_packet)

            out_packet.encode_byte(ServerRegistrationResponse.Valid)

            if server_type == ServerType.login:
                self._login = client
                self._login.port = 8484
                await client.send_packet_raw(out_packet)

            else:
                out_packet.encode_byte(valid_world.id)
                out_packet.encode_string("Kastia")

                if server_type == ServerType.shop:
                    self._shop = client
                    self._shop.port = 9595
                    out_packet.encode_short(9595)  # shop port

                else:
                    channel = valid_world.channels.add(client)
                    out_packet.encode_string("wee woo maplestory")
                    out_packet.encode_byte(channel.id)
                    out_packet.encode_short(channel.port)
                    out_packet.encode_byte(0)  # multi leveling
                    out_packet.encode_int(1)  # experience rate
                    out_packet.encode_int(1)  # quest experience
                    out_packet.encode_int(1)  # party quest experience
                    out_packet.encode_int(1)  # meso rate
                    out_packet.encode_int(1)  # drop rate

                await client.send_packet_raw(out_packet)

        client.type = server_type

        if client.type == ServerType.login:
            count = packet.decode_byte()

            for _ in range(count):
                world_id = packet.decode_byte()

                if not self._worlds.get(lambda w: w.id == world_id):
                    self._worlds.append(World(world_id).from_packet(packet))

            for world in self._worlds:
                for channel in world.channels:
                    with Packet(op_code=InterOps.UpdateChannel) as out_packet:
                        packet.encode_byte(channel.world.id)
                        packet.encode_byte(True)
                        packet.encode_byte(channel.id)
                        packet.encode_short(channel.port)
                        packet.encode_int(channel.population)

                        await self._login.send_packet_raw(out_packet)

            log.info("Registered Login Server on %s", self._login.port)

        elif client.type == ServerType.channel:
            with Packet(op_code=InterOps.UpdateChannel) as out_packet:
                out_packet.encode_byte(client.world.id)
                out_packet.encode_byte(True)
                out_packet.encode_byte(client.id)
                out_packet.encode_short(client.port)
                out_packet.encode_int(client.population)

                await self._login.send_packet_raw(out_packet)

    @packet_handler(InterOps.UpdateChannelPopulation)
    async def update_channel_population(self, client, packet):
        population = packet.decode_int()

        with Packet(op_code=InterOps.UpdateChannelPopulation) as out_packet:
            out_packet.encode_byte(client.world.id)
            out_packet.encode_byte(client.id)
            out_packet.encode_int(population)

            await self._login.send_packet_raw(out_packet)
