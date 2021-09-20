from dataclasses import dataclass, field
from typing import List

from common.abc import WildcardData

class Skill:
    def __init__(self, id):
        self._id = id
        self._skill_level_data = []

class SkillLevel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

@dataclass
class SkillLevelData(WildcardData):
    flags: List             = field(default=list)
    weapon: int             = 0
    sub_weapon: int         = 0
    max_level: int          = 0
    base_max_level: int     = 0
    skill_type: List        = field(default=list)
    element: str            = ""
    mob_count: str          = ""
    hit_count: str          = ""
    buff_time: str          = ""
    mp_cost: str            = ""
    hp_cost: str            = ""
    damage: str             = ""
    fixed_damage: str       = ""
    critical_damage: str    = ""
    mastery: str            = ""

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