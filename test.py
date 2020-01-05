from enum import Enum

class Meta(Enum):
    def __str__(self):
        return f"{str(self.name).lower()}"

class Schema(int, Meta):

    def __call__(cls, enum_name):
        def predicate(sub_elem):
            # enum_class = super().__init__(cls, sub_elem)  
            cls._value_ = sub_elem.value
            
            return cls

        return predicate

    def __new__(cls, name):
        def predicate(sub_elem):
            # enum_class = super().__init__(cls, name)  
            cls._value_ = sub_elem
            
            return enum_class

        return predicate

    def __init__(self, value):    
        cls = self.__class__
        pass

    def __str__(self):
        return f"{self.__class__.__name__.lower()}.{super().__str__()}"

        # self.__class__._value_ = value

class Table(Meta):
    def __new__(cls, data_type, options=None):
        value = len(cls.__members__) + 1
        enum_class = super().__new__(cls, value)
        
        enum_class._value_ = value
        enum_class.data_type = data_type

        return enum_class

class Bar(Schema):
    def __init__(self, sub_name):
        def predicate(sub_class):
            cls = self.__class__
            setattr(cls, sub_name, sub_class)

            return cls 

        predicate(sub_class)

@Bar('BAZ')
class Baz(Table):
    POOP = 1
    DOOP = 2

