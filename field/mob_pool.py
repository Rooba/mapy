from .object_pool import ObjectPool

class MobPool(ObjectPool):
    def __init__(self, field):
        super().__init__(field)
        self.spawns = []
    
    def add(self, mob):
        mob.field = self.field
        super().add(mob)
        self.spawns.append(mob)

    async def remove(self, key):
        mob = self.get(key)

        if mob:
            owner = None

            # await self.field.broadcast(CPacket.mob_leave_field(mob))

            if mob.dead:
                pass
                # drop_pos_x = mob.position.x
                # drop_pos_y = mob.position.y

                # self.field.drops.add(Drop(0, mob.position, 50, 1))
        
        return super().remove(key)