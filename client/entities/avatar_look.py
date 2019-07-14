from dataclasses import dataclass, field

@dataclass
class AvatarLook:
    gender: int = 0
    skin: int = 0
    face: int = 0
    hair: int = 0
    weapon_sticker_id: int = 0
    
    def __post_init__(self):
        f = lambda a: {str(i + 1): 0 for i in range(a)}
        self.equip = f(60)
        self.unseen_equip = f(60)
        self.pet_ids = [0 for i in range(3)]

    def encode(self, packet):
        packet.encode_byte(self.gender)
        packet.encode_byte(self.skin)
        packet.encode_int(self.face)
        packet.encode_byte(0)
        packet.encode_int(self.hair)

        AvatarLook.encode_inventory(packet, self.equip)
        AvatarLook.encode_inventory(packet, self.unseen_equip)

        packet.encode_int(0)

        for pet_id in self.pet_ids:
            packet.encode_int(pet_id)

    @staticmethod
    def encode_inventory(packet, inventory):
        for key, item in inventory.items():
            if item:
                packet.encode_byte(int(key))
                packet.encode_int(item)
        
        packet.encode_byte(0xFF)
    
    def copy(self, equipped):
        for slot in equipped:
            slot = int(slot) * -1

            if slot > 100:
                slot -= 100
            
            if self.equip[str(slot)]:
                continue

            self.equip[str(slot)] = equipped[str(slot * -1)]['item_id']