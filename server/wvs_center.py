from server._wvs_center import World, WorldManager
from server import ServerBase
from net.packets.opcodes import InterOps
from net.packets.packet import packet_handler, Packet
from client import WvsCenterClient
from common.enum import ServerType, ServerRegistrationResponse
from common import constants
from loguru import logger


class CenterServer(ServerBase):
    """Server connection listener for incoming client socket connections

    Attributes
    -----------
    is_alive: :class:`bool`
        Server alive status
    name: :class:`str`
        Server specific name
    login: :class:`LoginServer`
        Registered :class:`Login` Server
    _worlds: :class:`Worlds`[:class:`World`]
        List of registered :class:`World` clients
    shop: :class:`ShopServer`
        Connected `ShopServer`

    """

    __opcodes__ = InterOps

    def __init__(self):
        super().__init__('CenterServer')
        self._security_key = constants.CENTER_KEY
        self.login = None
        self._worlds = WorldManager(self, constants.WORLD_COUNT)
        self._shop = None

    async def client_connect(self, client):
        return WvsCenterClient(self, client)

    async def on_client_disconnect(self, client):
        if client == self.login:
            self.login = None

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

        packet = Packet(op_code=InterOps.RegistrationResponse)
        try:
                server_type = ServerType(server_type)
        except ValueError:
            packet.encode_byte(ServerRegistrationResponse.InvalidType)
            return await client.send_packet_raw(packet)

        if security_key != self._security_key:
            packet.encode_byte(ServerRegistrationResponse.InvalidCode)
            return await client.send_packet_raw(packet)

        valid_world = self._worlds.get_open()

        if server_type == ServerType.login and self.login or \
                server_type == ServerType.channel and not valid_world or \
                server_type == ServerType.shop and self._shop:
            packet.encode_byte(ServerRegistrationResponse.Full)
            return await client.send_packet_raw(packet)

        packet.encode_byte(ServerRegistrationResponse.Valid)

        if server_type == ServerType.login:
            self.login = client
            self.login.port = 8484
            await client.send_packet_raw(packet)

        else:
            packet.encode_byte(valid_world.id)
            packet.encode_string("Kastia")

            if server_type == ServerType.shop:
                self._shop = client
                self._shop.port = 9595
                packet.encode_short(9595)  # shop port

            else:
                channel = valid_world.channels.add(client)
                packet.encode_string("wee woo maplestory")
                packet.encode_byte(channel.id)
                packet.encode_short(channel.port)
                packet.encode_byte(0)  # multi leveling
                packet.encode_int(1)  # experience rate
                packet.encode_int(1)  # quest experience
                packet.encode_int(1)  # party quest experience
                packet.encode_int(1)  # meso rate
                packet.encode_int(1)  # drop rate

            await client.send_packet_raw(packet)

        client.type = server_type

        if client.type == ServerType.login:
            count = packet.decode_byte()

            for _ in range(count):
                world_id = packet.decode_byte()

                if not self._worlds.get(lambda w: w.id == world_id):
                    self._worlds.append(World(world_id).from_packet(packet))

            for world in self._worlds:
                for channel in world.channels:
                    with Packet(op_code=InterOps.UpdateChannel) as packet:
                        packet.encode_byte(channel.world.id)
                        packet.encode_byte(True)
                        packet.encode_byte(channel.id)
                        packet.encode_short(channel.port)
                        packet.encode_int(channel.population)

                        await self.login.send_packet_raw(packet)

            logger.info(f"Registered Login Server on --~{self.login.port}&")

        elif client.type == ServerType.channel:
            with Packet(op_code=InterOps.UpdateChannel) as packet:
                packet.encode_byte(client.world.id)
                packet.encode_byte(True)
                packet.encode_byte(client.id)
                packet.encode_short(client.port)
                packet.encode_int(client.population)

                await self.login.send_packet_raw(packet)

    @packet_handler(InterOps.UpdateChannelPopulation)
    async def update_channel_population(self, client, packet):
        population = packet.decode_int()

        with Packet(op_code=InterOps.UpdateChannelPopulation) as packet:
            packet.encode_byte(client.world.id)
            packet.encode_byte(client.id)
            packet.encode_int(population)

            await self.login.send_packet_raw(packet)
