import pydoc
import datetime
import decimal
import inspect

from .errors import SchemaError


class SQLType:
    python = type(None)

    def to_dict(self):
        dct = self.__dict__.copy()
        clas = self.__class__
        dct["__meta__"] = clas.__module__ + "." + clas.__qualname__
        return dct

    @classmethod
    def from_dict(cls, data):
        meta = data.pop("__meta__")
        given = cls.__module__ + "." + cls.__qualname__

        if given != meta:
            cls = pydoc.locate(meta)
            if cls is None:
                raise RuntimeError(f'Could not locate "{meta}".')

        self = cls.__new__(type(cls))
        self.__dict__.update(data)
        return self

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_sql(self):
        raise NotImplementedError()

    def is_real_type(self):
        return True


class Boolean(SQLType):
    python = bool

    def to_sql(self):
        return "BOOLEAN"


class Date(SQLType):
    python = datetime.date

    def to_sql(self):
        return "DATE"


class Datetime(SQLType):
    python = datetime.datetime

    def __init__(self, *, timezone=False):
        self.timezone = timezone

    def to_sql(self):
        if self.timezone:
            return "TIMESTAMP WITH TIMEZONE"

        return "TIMESTAMP"


class Double(SQLType):
    python = float

    def to_sql(self):
        return "REAL"


class Integer(SQLType):
    python = int

    def __init__(self, *, big=False, small=False, auto_increment=False):
        self.big = big
        self.small = small
        self.auto_increment = auto_increment

        if big and small:
            raise SchemaError("Integer cannot be both big and small")

    def to_sql(self):
        if self.auto_increment:
            if self.big:
                return "BIGSERIAL"
            if self.small:
                return "SMALLSERIAL"
            return "SERIAL"

        if self.big:
            return "BIGINT"
        if self.small:
            return "SMALLINT"
        return "INTEGER"

    def is_real_type(self):
        return not self.auto_increment


class Interval(SQLType):
    python = datetime.timedelta
    valid_fields = (
        "YEAR",
        "MONTH",
        "DAY",
        "HOUR",
        "MINUTE",
        "SECOND",
        "YEAR TO MONTH",
        "DAY TO HOUR",
        "DAY TO MINUTE",
        "DAY TO SECOND",
        "HOUR TO MINUTE",
        "HOUR TO SECOND",
        "MINUTE TO SECOND",
    )

    def __init__(self, field=None):
        if field:
            field = field.upper()
            if field not in self.valid_fields:
                raise SchemaError("invalid interval specified")

        self.field = field

    def to_sql(self):
        if self.field:
            return "INTERVAL " + self.field
        return "INTERVAL"


class Decimal(SQLType):
    python = decimal.Decimal

    def __init__(self, *, precision=None, scale=None):
        if precision is not None:
            if precision < 0 or precision > 1000:
                raise SchemaError("precision must be greater than 0 and below 1000")
            if scale is None:
                scale = 0

        self.precision = precision
        self.scale = scale

    def to_sql(self):
        if self.precision is not None:
            return f"NUMERIC({self.precision}, {self.scale})"
        return "NUMERIC"


class Numeric(SQLType):
    python = decimal.Decimal

    def __init__(self, *, precision=None, scale=None):
        if precision is not None:
            if precision < 0 or precision > 1000:
                raise SchemaError("precision must be greater than 0" "and below 1000")
            if scale is None:
                scale = 0

        self.precision = precision
        self.scale = scale

    def to_sql(self):
        if self.precision is not None:
            return f"NUMERIC({self.precision}, {self.scale})"
        return "NUMERIC"


class String(SQLType):
    python = str

    def __init__(self, *, length=None, fixed=False):
        self.length = length
        self.fixed = fixed

        if fixed and length is None:
            raise SchemaError("Cannot have fixed string with no length")

    def to_sql(self):
        if self.length is None:
            return "TEXT"
        if self.fixed:
            return f"CHAR({self.length})"
        return f"VARCHAR({self.length})"


class Time(SQLType):
    python = datetime.time

    def __init__(self, *, timezone=False):
        self.timezone = timezone

    def to_sql(self):
        if self.timezone:
            return "TIME WITH TIME ZONE"
        return "TIME"


class JSON(SQLType):
    python = None

    def to_sql(self):
        return "JSONB"


class ForeignKey(SQLType):
    def __init__(
        self,
        table,
        column,
        *,
        sql_type=None,
        on_delete="CASCADE",
        on_update="NO ACTION",
    ):
        if not table or not isinstance(table, str):
            raise SchemaError("Missing table to reference (must be string)")

        valid_actions = ("NO ACTION", "RESTRICT", "CASCADE", "SET NULL", "SET DEFAULT")

        on_delete = on_delete.upper()
        on_update = on_update.upper()

        if on_delete not in valid_actions:
            raise TypeError("on_delete must be one of %s." % valid_actions)

        if on_update not in valid_actions:
            raise TypeError("on_update must be one of %s." % valid_actions)

        self.table = table
        self.column = column
        self.on_update = on_update
        self.on_delete = on_delete

        if sql_type is None:
            sql_type = Integer

        if inspect.isclass(sql_type):
            sql_type = sql_type()

        if not isinstance(sql_type, SQLType):
            raise TypeError("Cannot have non-SQLType derived sql_type")

        if not sql_type.is_real_type():
            raise SchemaError('sql_type must be a "real" type')

        self.sql_type = sql_type.to_sql()

    def is_real_type(self):
        return False

    def to_sql(self):
        return (
            f"{self.column} REFERENCES {self.table} ({self.column})"
            f" ON DELETE {self.on_delete} ON UPDATE {self.on_update}"
        )


class ArraySQL(SQLType):
    def __init__(self, inner_type, size: int | None = None):
        if not isinstance(inner_type, SQLType):
            raise SchemaError("Array inner type must be an SQLType")
        self.type = inner_type
        self.size = size

    def to_sql(self):
        if self.size:
            return f"{self.type.to_sql()}[{self.size}]"
        return f"{self.type.to_sql()}[]"
