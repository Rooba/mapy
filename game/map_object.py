from dataclasses import dataclass 

from common.abc import WildcardData

class MapObject(WildcardData):
    obj_id: int = -1
    