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
    _levels: int = 0
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
