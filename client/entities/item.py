from enum import Enum

class ItemInventoryTypes(Enum):
    ItemSlotEquip = 0x1

class ItemSlotBase:
    def __init__(self, *, item_id=None, cisn=None, 
                    expire=None, inventory_item_id=None):
        
        self.item_id: int = item_id # temaplate_id
        self.cash_item_sn: int = cisn
        self.expire: int = expire
        self.inv_item_id: int = inventory_item_id # database relation

    def encode(self, packet):
        packet.encode_int(self.item_id)
        packet.encode_bool(not self.cash_item_sn)

        if self.cash_item_sn:
            packet.encode_long(self.cash_item_sn)

        packet.encode_long(self.expire)

class ItemSlotEquip(ItemSlotBase):
    def __init__(self, item_id=None, cisn=None, expire=None, 
                inventory_item_id=None, **kwargs) -> object:
        super().__init__(item_id=item_id, cisn=cisn, expire=expire, 
                inventory_item_id=inventory_item_id)

        self.ruc = kwargs.get('ruc')
        self.cuc = kwargs.get('cuc')

        self.str = kwargs.get('str')
        self.dex = kwargs.get('dex')
        self.int = kwargs.get('int')
        self.luk = kwargs.get('luk')
        self.hp = kwargs.get('hp')
        self.mp = kwargs.get('mp')
        self.watk = kwargs.get('watk')
        self.matk = kwargs.get('matk')
        self.wdef = kwargs.get('wdef')
        self.mdef = kwargs.get('mdef')
        self.acc = kwargs.get('acc')
        self.avoid = kwargs.get('avoid')
        
        self.hands = kwargs.get('hands')
        self.speed = kwargs.get('speed')
        self.jump = kwargs.get('jump')

        self.title = kwargs.get('owner')
        self.craft = kwargs.get('craft')
        self.attribute = kwargs.get('attribute')
        self.level_up_type = kwargs.get('level_up_type')
        self.level = kwargs.get('level')
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
        packet.encode_int(0) # durability woops
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