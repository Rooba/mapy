from attrs import define, field


class Skill:
    def __init__(self, id):
        self._id = id
        self._skill_level_data = []


class SkillLevel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@define
class SkillLevelData(object):
    flags: list[int] = field(factory=list)
    weapon: int = 0
    sub_weapon: int = 0
    max_level: int = 0
    base_max_level: int = 0
    skill_type: list = field(factory=list)
    element: str = field(factory=str)
    mob_count: str = field(factory=str)
    hit_count: str = field(factory=str)
    buff_time: str = field(factory=str)
    mp_cost: str = field(factory=str)
    hp_cost: str = field(factory=str)
    damage: str = field(factory=str)
    fixed_damage: str = field(factory=str)
    critical_damage: str = field(factory=str)
    mastery: str = field(factory=str)

    def __post_init__(self):
        self._levels = {}
        for i in range(self.max_level):
            kwargs = {}
            for name, value in self.__dict__.items():
                if isinstance(value, str):
                    # kwargs[name] = rtl_equation(value, i)
                    pass
                else:
                    kwargs[name] = value

            self._levels[i] = SkillLevel(**kwargs)

    def __getitem__(self, index):
        return self._levels[index]


# @dataclass
# class SkillLevel(WildcardData):
#     max_level:int           = 0
#     mob_count:int           = 0
#     hit_count:int           = 0
#     range:int               = 0
#     buff_time:int           = 0
#     cost_hp:int             = 0
#     cost_mp:int             = 0
#     damage:int              = 0
#     fixed_damage:int        = 0
#     critical_damage:int     = 0
#     mastery:int             = 0
#     option_item_cost:int    = 0
#     item_cost:int           = 0
#     item_count:int          = 0
#     bullet_cost:int         = 0
#     meso_cost:int           = 0
#     parameter_a:int         = 0
#     parameter_b:int         = 0
#     speed:int               = 0
#     jump:int                = 0
#     strength:int            = 0
#     weapon_attack:int       = 0
#     weapon_defense:int      = 0
#     magic_attack:int        = 0
#     magic_defense:int       = 0
#     accuracy:int            = 0
#     avoid:int               = 0
#     hp:int                  = 0
#     mp:int                  = 0
#     probability:int         = 0
#     morph:int               = 0
#     cooldown:int            = 0
#     ltx:int                 = 0
#     lty:int                 = 0
#     rbx:int                 = 0
#     rby:int                 = 0
