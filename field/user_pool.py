from .object_pool import ObjectPool


class UserPool(ObjectPool):
    def add(self, client):
        super().add(client)
        client.character.field = self.field

    @property
    def characters(self):
        return [client.character for client in self]

    def __aiter__(self):
        return [client for client in self]
