from dataclasses import dataclass, InitVar

@dataclass
class CharacterStat:
    id: int = 0
    account_id: int = 0
    name: str = ""
    gender: int = 0
    skin: int = 0
    face: int = 0
    hair: int = 0
    level: int = 0
    job: int = 0
    str: int = 0
    dex: int = 0
    int: int = 0
    luk: int = 0
    hp: int = 0
    m_hp: int = 0
    mp: int = 0
    m_mp: int = 0
    ap: int = 0
    sp: int = 0
    exp: int = 0
    fame: int = 0
    money: int = 0
    temp_exp: int = 0
    pos_map: int = 0
    portal: int = 0
    play_time: int = 0
    sub_job: int = 0
    extend_sp: InitVar = None
    pet_locker: InitVar = None

    def __post_init__(self, extend_sp=None, pet_locker=None):
        f = lambda a: [0 for _ in range(a)]
        self.extend_sp = f(9) if not extend_sp else extend_sp
        self.pet_locker = f(3) if not pet_locker else pet_locker

    def encode(self, packet):
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
        packet.encode_int(self.pos_map)
        packet.encode_byte(self.portal)
        packet.encode_int(self.play_time)
        packet.encode_short(self.sub_job)