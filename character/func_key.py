from dataclasses import dataclass

@dataclass
class FuncKey:
    type: int
    action: int

class FuncKeys:
    def __init__(self, character):
        self._parent = character
        self._func_keys = {}

    def __setitem__(self, key, value):
        self._func_keys[key] = value
    
    def __getitem__(self, key):
        return self._func_keys.get(key, FuncKey(0, 0))
    

