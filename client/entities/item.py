from enum import Enum

class ItemInventoryTypes(Enum):
    ItemSlotEquip = 0x1

class ItemSlotBase:
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

    def __init__(self, *, item_id=None, cisn=None, 
                    expire=None, inventory_item_id=None,
                    flag=0, quantity=1):
        
        self.item_id = item_id # temaplate_id
        self.cisn = cisn
        self.expire = expire
        self.inventory_item_id = inventory_item_id
        # self.price = price
        self.quantity = quantity
        self.flag = flag

    def encode(self, packet) -> None:
        """Encode base item information onto packet
        
        Parameters
        ----------
        packet: :class:`net.packets.Packet`
            The packet to encode the data onto

        """

        packet.encode_int(self.item_id)
        packet.encode_bool(not self.cisn)

        if self.cisn:
            packet.encode_long(self.cisn)

        packet.encode_long(self.expire)

class ItemSlotEquip(ItemSlotBase):
    def __init__(self, item_id=None, cisn=None, expire=None, 
                inventory_item_id=None, **kwargs) -> object:
        super().__init__(item_id=item_id, cisn=cisn, expire=expire, 
                inventory_item_id=inventory_item_id)

        self.req_job = kwargs.get('req_job', [0])

        # equip_slots returns list[string] need 
        # to convert to list[int]

        self.ruc = kwargs.get('ruc', 0)
        self.cuc = kwargs.get('cuc', 0)

        self.str = kwargs.get('str', 0)
        self.dex = kwargs.get('dex', 0)
        self.int = kwargs.get('int', 0)
        self.luk = kwargs.get('luk', 0)
        self.hp = kwargs.get('hp', 0)
        self.mp = kwargs.get('mp', 0)
        self.watk = kwargs.get('watk', 0)
        self.matk = kwargs.get('matk', 0)
        self.wdef = kwargs.get('wdef', 0)
        self.mdef = kwargs.get('mdef', 0)
        self.acc = kwargs.get('acc', 0)
        self.avoid = kwargs.get('avoid', 0)
        
        self.hands = kwargs.get('hands', 0)
        self.speed = kwargs.get('speed', 0)
        self.jump = kwargs.get('jump', 0)

        self.title = kwargs.get('owner', "")
        self.craft = kwargs.get('craft')
        self.attribute = kwargs.get('attribute')
        self.level_up_type = kwargs.get('level_up_type')
        self.level = kwargs.get('level')
        self.durability = kwargs.get('durability', -1)
        self.iuc = kwargs.get('iuc')
        self.exp = kwargs.get('exp')

        self.grade = kwargs.get('grade')
        self.chuc = kwargs.get('chuc')

        self.option_1 = kwargs.get('option_1')
        self.option_2 = kwargs.get('option_2')
        self.option_3 = kwargs.get('option_3')
        self.socket_1 = kwargs.get('socket_1')
        self.socket_2 = kwargs.get('socket_2')

        self.lisn = kwargs.get('lisn')
        self.storage_id = kwargs.get('storage_id')
        self.sn = kwargs.get('sn')
    
    def encode(self, packet):
        packet.encode_byte(1)

        super().encode(packet)

        packet.encode_byte(self.ruc)
        packet.encode_byte(self.cuc)
        packet.encode_short(self.str)
        packet.encode_short(self.dex)
        packet.encode_short(self.int)
        packet.encode_short(self.luk)
        packet.encode_short(self.hp)
        packet.encode_short(self.mp)
        packet.encode_short(self.watk)
        packet.encode_short(self.matk)
        packet.encode_short(self.wdef)
        packet.encode_short(self.mdef)
        packet.encode_short(self.acc)
        packet.encode_short(self.avoid)
        packet.encode_short(self.craft)
        packet.encode_short(self.speed)
        packet.encode_short(self.jump)
        packet.encode_string(self.title)
        packet.encode_short(self.attribute)

        packet.encode_byte(self.level_up_type)
        packet.encode_byte(self.level)
        packet.encode_int(self.durability)
        packet.encode_int(self.iuc)
        packet.encode_byte(self.grade)
        packet.encode_byte(self.chuc)
        packet.encode_short(self.option_1)
        packet.encode_short(self.option_2)
        packet.encode_short(self.option_3)
        packet.encode_short(self.socket_1)
        packet.encode_short(self.socket_2)
        
        if not self.cash_item_sn:
            packet.encode_long(self.lisn)
    
        packet.encode_long(150841440000000000)
        packet.encode_int(-1)


class ItemSlotBundle(ItemSlotBase):
    pass

