from attrs import define, field


def default_extend_sp():
    return [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]


def default_pet_locker():
    return [ 0, 0, 0 ]


@define
class CharacterStats(object):
    id: int = 0
    name: str = ""
    world_id: int = 0

    gender: int = 0
    skin: int = 0
    face: int = field(default=20001)
    hair: int = field(default=30003)
    level: int = field(default=1)
    job: int = 0

    str_: int = field(default=4)
    dex: int = field(default=4)
    int_: int = field(default=4)
    luk: int = field(default=4)
    hp: int = field(default=50)
    m_hp: int = field(default=50)
    mp: int = field(default=5)
    m_mp: int = field(default=5)

    ap: int = 0
    sp: int = 0
    extend_sp: list[int] = field(factory=default_extend_sp)

    exp: int = 0
    money: int = 0
    fame: int = 0
    temp_exp: int = 0

    field_id: int = field(default=100000000)
    portal: int = 0
    play_time: int = 0
    sub_job: int = 0
    pet_locker: list[int] = field(factory=default_pet_locker)

    def encode(self, packet) -> None:
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
        packet.encode_short(self.str_)
        packet.encode_short(self.dex)
        packet.encode_short(self.int_)
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
