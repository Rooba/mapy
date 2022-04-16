class CharacterSkills(dict):
    def __init__(self, parent):
        self._parent = parent

    async def cast(self, skill_id):
        skill = self.get(skill_id)

        if not skill:
            return False

        await self._parent.modify.stats(
            hp=self._parent.stats.hp - 1, mp=self._parent.stats.mp - 1
        )

        # if skill.level_data.buff_time > 0:
        #     await self._parent.buffs.remove(skill.id)

        #     buff = Buff(skill.id)
        #     buff.generate(skill.level_data)

        #     await self._parent.buff.add(buff)

        return True
