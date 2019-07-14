from .inventory import InventoryManager, InventoryType
from . import item as Item
from utils import filter_out_to

class Character:
    def __init__(self, **data):
        f = lambda a: [0 for _ in range(a)]

        self.id: int = data.get('character_id', 1000)
        self.name: str = data.get('name', "Mapler")

        self.gender: int = data.get('gender', 0)
        self.skin: int = data.get('skin', 0)
        self.face: int = data.get('face', 20001)
        self.hair: int = data.get('hair', 30003)

        self.level: int = data.get('level', 1)
        self.job: int = data.get('job', 0)
        self.str: int = data.get('str', 4)
        self.dex: int = data.get('dex', 4)
        self.int: int = data.get('int', 4)
        self.luk: int = data.get('luk', 4)

        self.hp: int = data.get('hp', 50)
        self.m_hp: int = data.get('m_hp', 50)
        self.mp: int = data.get('mp', 5)
        self.m_mp: int = data.get('m_mp', 5)

        self.ap: int = data.get('ap', 0)
        self.sp: int = data.get('sp', 0)
        self.extend_sp = data.get('extend_sp', f(9))

        self.exp: int = data.get('exp', 0)
        self.money: int = data.get('money', 0)
        self.fame: int = data.get('fame', 0)

        self.temp_exp: int = data.get('temp_exp', 0)
        self.field_id: int = data.get('pos_map', 100000000)
        self.portal: int = data.get('portal', 0)
        self.play_time: int = data.get('play_time', 0)
        self.sub_job: int = data.get('sub_job', 0)
        self.pet_locker = data.get('pet_locker', f(3))
        self.pet_ids = f(3)

        self.inventories = InventoryManager()
    
    @staticmethod
    def from_data(**data):
        character = Character(**data)
        
        for key, inv in data.get('inventories').items():
            for item_ in inv:
                type_ = InventoryType(int(item_['item_id'] / 1000000)) 
                
                item = getattr(Item, Item.ItemInventoryTypes(type_.value).name)(**item_)
                
                character.inventories[InventoryType(type_).value].add(item, int(item_['position']))
        
        return character

    def encode_stats(self, packet):
        packet.encode_int(self.id)
        packet.encode_fixed_string(self.name, 13)
        packet.encode_byte(self.gender)
        packet.encode_byte(self.skin)
        packet.encode_int(self.face)
        packet.encode_int(self.hair)

        for sn in self.pet_locker:
            packet.encode_long(sn)
        
        packet.encode_byte(self.level)
        packet.encode_short(self.job)
        packet.encode_short(self.str)
        packet.encode_short(self.dex)
        packet.encode_short(self.int)
        packet.encode_short(self.luk)
        packet.encode_int(self.hp)
        packet.encode_int(self.m_hp)
        packet.encode_int(self.mp)
        packet.encode_int(self.m_mp)
        packet.encode_short(self.ap)

        # if player not evan
        packet.encode_short(self.sp)
        # else
            # packet.encode_byte(len(self.extend_sp))

            # for i, sp in enumerate(self.extend_sp):
            #     packet.encode_byte(i)
            #     packet.encode_byte(sp)
        
        packet.encode_int(self.exp)
        packet.encode_short(self.fame)
        packet.encode_int(self.temp_exp)
        packet.encode_int(self.field_id)
        packet.encode_byte(self.portal)
        packet.encode_int(self.play_time)
        packet.encode_short(self.sub_job)
    
    def encode_look(self, packet):

        packet.encode_byte(self.gender)
        packet.encode_byte(self.skin)
        packet.encode_int(self.face)
        packet.encode_byte(0)
        packet.encode_int(self.hair)

        inventory = self.inventories.get(InventoryType.equip)
        equipped = dict(
            filter(
                lambda item: item[0] < 0,
                inventory.items.items()
            )
        )
        unseen = []

        stickers = filter_out_to(
            lambda item: not equipped.get(item[0] - 100) if item[0] > -100 else True,
            equipped.items(),
            unseen
        )

        map(lambda item: (item[0] - 100, item[1]) if item[0] > -100 else item, unseen)

        for inv in [stickers, unseen]:
            for item in inv:
                packet.encode_byte(item[0] * -1).encode_int(item[1].item_id)
            
            packet.encode_byte(0xFF)

        packet.encode_int(0 if not equipped.get(-111) else equipped[-111].item_id)

        for pet_id in self.pet_ids:
            packet.encode_int(pet_id)
