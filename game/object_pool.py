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
        return (obj for obj in self.cache.values())

    def __iter__(self):
        return (obj for obj in self.cache.values())