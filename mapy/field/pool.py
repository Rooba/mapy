class ObjectPool:

    def __init__(self, field):
        self.field = field
        self.cache = {}
        self.uid_base = 1000

    @property
    def new_uid(self):
        self.uid_base += 1
        return self.uid_base

    def add(self, value):
        value.obj_id = self.new_uid
        self.cache[value.obj_id] = value

    def remove(self, key):
        return self.cache.pop(key)

    def clear(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key, None)

    def __enumerator__(self):
        return ( obj for obj in self.cache.values() )

    def __iter__(self):
        return ( obj for obj in self.cache.values() )

    def __aiter__(self):
        return self.__iter__()


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


class NpcPool(ObjectPool):
    ...


class UserPool(ObjectPool):

    def add(self, client):
        super().add(client)
        client.character.field = self.field

    @property
    def characters(self):
        return [client.character for client in self]

    def __aiter__(self):
        return [ client for client in self ]
