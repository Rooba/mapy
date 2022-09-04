from enum import Enum
from uuid import UUID, uuid4

from attrs import define


class ItemInventoryTypes(Enum):
    ItemSlotEquip = 0x1


@define
class ItemSlotBase(object):
    """Base item class for all items

    Parameters
    ----------
    item_id: int
        Item temaplte ID
    cisn: int
        Cash Inventory Serial Numer
        Used for tracking cash items
    expire: :class:`datetime.datetime`
        Expiry date of the item, if any
    inventory_item_id: int
        Primary key to store the item in database
    flag: bool
        Determines whether item has been deleted,
        transfered, or stayed in inventory

    """

    item_id: int = 0
    item_uuid: UUID = uuid4()
    source_type: int = 0
    expire: int = 0
    quantity: int = 0
    flag: int = 0

    def encode(self, packet) -> None:
        """Encode base item information onto packet

        Parameters
        ----------
        packet: :class:`net.packets.Packet`
            The packet to encode the data onto

        """

        packet.encode_int(self.item_id)
        packet.encode_byte(self.cisn == 0)

        if self.cisn:
            packet.encode_long(self.cisn)

        packet.encode_long(0)


@define
class ItemSlotEquip(ItemSlotBase):
    req_job: list[int] | None = list()
    ruc: int = 0
    cuc: int = 0

    _str: int = 0
    dex: int = 0
    _int: int = 0
    luk: int = 0
    hp: int = 0
    mp: int = 0
    weapon_attack: int = 0
    weapon_defense: int = 0
    magic_attack: int = 0
    magic_defense: int = 0
    accuracy: int = 0
    avoid: int = 0

    hands: int = 0
    speed: int = 0
    jump: int = 0

    title: str = ""
    craft: int = 0
    attribute: int = 0
    level_up_type: int = 0
    level: int = 0
    durability: int = 0
    iuc: int = 0
    exp: int = 0

    grade: int = 0
    chuc: int = 0

    option_1: int = 0
    option_2: int = 0
    option_3: int = 0
    socket_1: int = 0
    socket_2: int = 0

    lisn: int = 0
    storage_id: int = 0
    sn: int = 0

    def encode(self, packet):
        packet.encode_byte(1)

        super().encode(packet)

        packet.encode_byte(self.ruc)
        packet.encode_byte(self.cuc)
        packet.encode_short(self._str)
        packet.encode_short(self.dex)
        packet.encode_short(self._int)
        packet.encode_short(self.luk)
        packet.encode_short(self.hp)
        packet.encode_short(self.mp)
        packet.encode_short(self.weapon_attack)
        packet.encode_short(self.magic_attack)
        packet.encode_short(self.weapon_defense)
        packet.encode_short(self.magic_defense)
        packet.encode_short(self.accuracy)
        packet.encode_short(self.avoid)
        packet.encode_short(self.craft)
        packet.encode_short(self.speed)
        packet.encode_short(self.jump)
        packet.encode_string(self.title)
        packet.encode_short(self.attribute)

        packet.encode_byte(self.level_up_type)
        packet.encode_byte(self.level)
        packet.encode_int(self.exp)
        packet.encode_int(-1 & 0xFFFFFF)

        packet.encode_int(self.iuc)

        packet.encode_byte(self.grade)
        packet.encode_byte(self.chuc)

        packet.encode_short(self.option_1)
        packet.encode_short(self.option_2)
        packet.encode_short(self.option_3)
        packet.encode_short(self.socket_1)
        packet.encode_short(self.socket_2)

        if not self.cisn:
            packet.encode_long(0)

        packet.encode_long(0)
        packet.encode_int(0)


@define
class ItemSlotBundle(ItemSlotBase):
    number: int = 1
    attribute: int = 0
    lisn: int = 0
    title: str = ""

    def encode(self, packet):
        packet.encode_byte(2)

        super().encode(packet)

        packet.encode_short(self.number)
        packet.encode_string(self.title)
        packet.encode_short(self.attribute)

        if self.item_id / 10000 == 207:
            packet.encode_long(self.lisn)
