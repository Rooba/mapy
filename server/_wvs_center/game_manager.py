from common.constants import GAME_PORT

class ChannelManager(list):
    def __init__(self, world, max_ = -1):
        self._world = world
        self._max = max_

    def get(self, identifier):
        return next((client for client in self if client.identifier == identifier), None)
        
    def add(self, client):
        if len(self) >= self._max and self._max != -1:
            print(f"{self._world.name} cannot hold anymore {client.name}s")
        
        elif client in self:
            print(f"{client.name} {client.identifier} is already in {self._world.name}")
        
        else:
            self.append(client)

            client.port = GAME_PORT + len(self)
            client.world = self._world
            client.id = len(self) - 1
        
        return client
    
    @property
    def is_full(self):
        return len(self) >= self._max if self._max != -1 else False