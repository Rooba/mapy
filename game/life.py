from dataclasses import dataclass 

from .map_object import MapObject


@dataclass
class Life(MapObject):
    life_id: int    = 0
    type: str       = ""
    foothold: int   = 0
    x: int          = 0
    y: int          = 0
    cy: int         = 0
    f: int          = 0
    hide: int       = 0
    rxo: int        = 0 # min click position
    rx1: int        = 0 # max click position
    mob_time: int   = 0    
        
