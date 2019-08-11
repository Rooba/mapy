class WorldManager(list):
    def __init__(self, WvsCenter, world_count=1):
        self._world_count = world_count

    def get_open(self):
        for world in self:
            if not world.channels.is_full:
                return world

        return None

    def get(self, world_id):
        for world in self:
            if world.id == world_id:
                return world

        return None

    @property
    def registered_worlds(self):
        return sum([1 for world in self])
