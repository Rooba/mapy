from dataclasses import dataclass

from .field_object import FieldObject


@dataclass
class Life(FieldObject):
    life_id: int = 0
    life_type: str = ""
    foothold: int = 0
    x: int = 0
    y: int = 0
    cy: int = 0
    f: int = 0
    hide: int = 0
    rx0: int = 0  # min click position
    rx1: int = 0  # max click position
    mob_time: int = 0
