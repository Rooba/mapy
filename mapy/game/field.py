from math import atan, cos
from random import choice
from typing import Type

from attrs import define, field

from ..abstract import ObjectPool
from ..cpacket import CPacket
from ..packet import ByteBuffer
from ..tools import TagPoint


class MovePath:
    def __init__(self, x=0, y=0, foothold=0, position=0):
        self.x = x
        self.y = y
        self.foothold = foothold
        self.stance = position
        self.vx = None
        self.vy = None

    def decode_move_path(self, move_path):
        ipacket = ByteBuffer(move_path)

        self.x = ipacket.decode_short()
        self.y = ipacket.decode_short()
        self.vx = ipacket.decode_short()
        self.vy = ipacket.decode_short()

        size = ipacket.decode_byte()

        for _ in range(size):
            cmd = ipacket.decode_byte()

            if cmd == 0:
                self.x = ipacket.decode_short()
                self.y = ipacket.decode_short()
                _ = ipacket.decode_short()  # xwob
                _ = ipacket.decode_short()  # ywob
                self.foothold = ipacket.decode_short()
                _ = ipacket.decode_short()  # xoff
                _ = ipacket.decode_short()  # yoff
                self.stance = ipacket.decode_byte()
                _ = ipacket.decode_short()  # duration
            elif cmd == 1:
                _ = ipacket.decode_short()  # xmod
                _ = ipacket.decode_short()  # ymod
                self.stance = ipacket.decode_short()
                _ = ipacket.decode_short()  # duration
            elif cmd == 27:
                self.stance = ipacket.decode_byte()
                _ = ipacket.decode_short()  # unk
            else:
                break

    def __str__(self):
        return (
            f"Position: {self.x},{self.y} - Foothold: {self.foothold} "
            f"- Stance: {self.stance}"
        )


@define
class FieldObject(object):
    _obj_id: int = -1
    _position: MovePath = MovePath()
    _field: Type["Field"] | None = None


@define
class Foothold(object):
    id: int = 0
    prev: int = 0
    next: int = 0
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0

    @property
    def wall(self):
        return self.x1 == self.x2

    def compare_to(self, foothold):
        if self.y2 < foothold.y1:
            return -1
        if self.y1 > foothold.y2:
            return 1
        return 0


@define
class Portal(object):
    _id: int = field(default=0)
    name: str = ""
    _type: int = field(default=0)
    destination: int = 0
    destination_label: str = ""
    x: int = 0
    y: int = 0

    def __init__(
        self,
        id: int = 0,
        name: str = "",
        type_: int = 0,
        destination: int = 0,
        destination_label: str = "",
        x: int = 0,
        y: int = 0,
    ):
        self.id = id
        self.name = name or ""
        self.type = type_
        self.destination = destination
        self.destination_label = destination_label or ""
        self.x = x
        self.y = y
        self.point = TagPoint(self.x, self.y)

    def __str__(self):
        return f"{id} @ {self.point} -> {self.destination}"


@define
class Life(FieldObject):
    def __init__(
        self,
        life_id: int = 0,
        life_type: str = "",
        foothold: int = 0,
        x: int = 0,
        y: int = 0,
        cy: int = 0,
        f: int = 0,
        hide: int = 0,
        rx0: int = 0,
        rx1: int = 0,
        mob_time: int = 0,
        **_,
    ):
        self.life_id: int = life_id
        self.life_type: str = life_type or ""
        self.foothold: int = foothold
        self.x: int = x
        self.y: int = y
        self.cy: int = cy
        self.f: int = f
        self.hide: int = hide
        self.rx0: int = rx0  # min click position
        self.rx1: int = rx1  # max click position
        self.mob_time: int = 0


@define
class Mob(Life):
    mob_id: int = 0
    hp: int = 0
    mp: int = 0
    hp_recovery: int = 0
    mp_recovery: int = 0
    exp: int = 0
    physical_attack: int = 0

    def __init__(
        self,
        mob_id: int = 0,
        hp: int = 0,
        mp: int = 0,
        hp_recovery: int = 0,
        mp_recovery: int = 0,
        exp: int = 0,
        physcial_attack: int = 0,
        **data,
    ):
        super().__init__(**data)
        self.mob_id = mob_id
        self.hp = hp
        self.hp_recovery = hp_recovery
        self.mp = mp
        self.mp_recovery = mp_recovery
        self.exp = exp
        self.physical_attack = physcial_attack
        self.attackers = {}
        self.pos = MovePath(self.x, self.cy, self.foothold)
        self.cur_hp = self.hp
        self.cur_mp = self.mp
        self.controller = None

    @property
    def dead(self):
        return self.cur_hp <= 0

    def damage(self, character, amount):
        pass

    def encode_init(self, packet):
        packet.encode_int(self._obj_id)
        packet.encode_byte(5)
        packet.encode_int(self.life_id)

        # Set Temporary Stat
        packet.encode_long(0)
        packet.encode_long(0)

        packet.encode_short(self.pos.x)
        packet.encode_short(self.pos.y)
        packet.encode_byte(0 & 1 | 2 * 2)
        packet.encode_short(self.pos.foothold)
        packet.encode_short(self.pos.foothold)

        packet.encode_byte(abs(-2))

        packet.encode_byte(0)
        packet.encode_int(0)
        packet.encode_int(0)


@define
class Npc(Life):
    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.life_id
        self.pos = MovePath(self.x, self.cy, self.foothold)


class Field:
    def __init__(self, map_id):
        self.map_id = map_id
        # self.characters = []
        # self.sockets = {}

        self.portals = PortalManager()
        self.footholds = FootholdManager()
        self.clients = UserPool(self)
        self.mobs = MobPool(map_id)
        self.npcs = NpcPool(map_id)

    @property
    def id(self):
        return self.map_id

    async def add(self, client):
        character = client.character

        if client.sent_char_data:
            await client.send_packet(
                CPacket.set_field(character, False, client.channel_id)
            )

        else:
            client.sent_char_data = True
            character.stats.portal = 0

            await client.send_packet(
                CPacket.set_field(character, True, client.channel_id)
            )

        for _character in self.clients.characters:
            await client.send_packet(CPacket.user_enter_field(_character))

        await self.spawn_mobs(client)
        await self.spawn_npcs(client)

        self.clients.add(client)

        await self.broadcast(CPacket.user_enter_field(character))

    async def broadcast(self, packet, *ignore):
        for client in self.clients:
            if client in ignore or client.character in ignore:
                continue

            await client.send_packet(packet)

    async def swap_mob_controller(self, client, mob):
        if mob.controller:
            controller = next(
                filter(
                    lambda c: c.character.id == mob.controller, ()
                ),  # FIXME: IDRCC WHERE WE'RE GRABBIN THIS SHIT ITS SOMEWHERE IN THERE
                None,
            )
            if controller:
                await controller.send_packet(CPacket.mob_change_controller(mob, 0))

        mob.controller = client.character.id
        await client.send_packet(CPacket.mob_change_controller(mob, 1))

    async def spawn_mobs(self, client):
        for mob in self.mobs:
            if mob.controller == 0:
                await self.swap_mob_controller(client, mob)

            await client.send_packet(CPacket.mob_enter_field(mob))

    async def spawn_npcs(self, client):
        for npc in self.npcs:
            await client.send_packet(CPacket.npc_enter_field(npc))


class MobPool(ObjectPool):
    def __init__(self, field):
        super().__init__(field)
        self.spawns = []

    def add(self, mob):
        mob.field = self.field
        super().add(mob)
        self.spawns.append(mob)

    async def remove(self, key):
        mob = self.get(key)

        if mob:
            _ = None  # owner

            # await self.field.broadcast(CPacket.mob_leave_field(mob))

            if mob.dead:
                pass
                # drop_pos_x = mob.position.x
                # drop_pos_y = mob.position.y

                # self.field.drops.add(Drop(0, mob.position, 50, 1))

        return super().remove(key)


class NpcPool(ObjectPool):
    ...


class UserPool(ObjectPool):
    def add(self, client):
        super().add(client)
        client.character.field = self.field

    @property
    def characters(self):
        return [client.character for client in self]

    def __aiter__(self):
        return [client for client in self]


class PortalManager:
    def __init__(self):
        self.portals = []

    def add(self, portal):
        self.portals.append(portal)

    def __filter_portals(self, name):
        return filter(lambda p: p.name == name, self.portals)

    def get_portal(self, name):
        return next(self.__filter_portals(name), None)

    def get_random_spawn(self):
        portals = list(self.__filter_portals("sp"))

        return choice(portals).id if portals else 0


class FootholdManager:
    def __init__(self):
        self.footholds = []

    def add(self, foothold):
        self.footholds.append(foothold)

    def find_below(self, tag_point):
        matches = []

        for foothold in self.footholds:
            if foothold.x1 <= tag_point.x and foothold.x2 >= tag_point.x:
                matches.append(foothold)

        for foothold in matches:
            if not foothold.wall and foothold.y1 != foothold.y2:
                s1 = foothold.y2 - foothold.y1
                s2 = foothold.x2 - foothold.x1
                s4 = tag_point.x - foothold.x1
                alpha = atan(s2 / s1)
                beta = atan(s1 / s2)
                s5 = cos(alpha) * (s4 / cos(beta))

                if foothold.y2 < foothold.y2:
                    calcy = foothold.y1 - int(s5)
                else:
                    calcy = foothold.y1 + int(s5)

                if calcy >= tag_point.y:
                    return foothold

            elif not foothold.wall and foothold.y1 >= tag_point.y:
                return foothold

        return None
