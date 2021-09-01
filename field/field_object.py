from dataclasses import dataclass 

from common.abc import WildcardData
from .move_path import MovePath
from utils import log


class FieldObject(WildcardData):
    def __init__(self):
        self._obj_id = -1
        self._position = MovePath()
        self._field = None
    
    @property
    def obj_id(self):
        return self._obj_id

    @obj_id.setter
    def obj_id(self, value):
        self._obj_id = value
    
    @property
    def position(self):
        return self._position

    @property
    def field(self):
        return self._field
    
    @field.setter
    def field(self, value):
        self._field = value