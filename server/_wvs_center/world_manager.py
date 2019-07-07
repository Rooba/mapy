from asyncio import Lock

from common.enum import ServerType

class WorldManager(list):
    def __init__(self, WvsCenter, world_count = 1):
        self._lock = Lock()
        self._parent = WvsCenter
        self._world_count = world_count
        self._worlds = {str(i): None for i in range(self._world_count)}
    
    def append(self, item):
        if len(self) >= self._world_count:
            raise IndexError(f"World server at max of {self._world_count} already")
        
        super().append(item)
        for key in self._worlds:
            if not self._worlds[key]:
                self._worlds[key] = item
    
    def pop(self, index):
        item = super().pop(index)

        for key in self._worlds:
            if self._worlds[key] == item:
                self._worlds[key] = None

    async def get_open(self):
        async with self._lock:
            for world in self:
                if not world.channels.is_full:
                    return world
                
                continue
            
            return None

    @property
    def worlds(self):
        return self._worlds

    @property
    def registered_worlds(self):
        return sum([1 for world in self._worlds if self._worlds[world]])
    
