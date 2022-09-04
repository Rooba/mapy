#  type: ignore
from itertools import chain, zip_longest
from typing import Any

from .errors import QueryError, ResponseError, SchemaError
from .types import (
    ArraySQL,
    Boolean,
    Datetime,
    Decimal,
    Integer,
    Interval,
    SQLType,
    String,
)


def default_tmpl(c, o, v):
    return f"{c} {o} {v}"


class SQLOperator:
    def __init__(
        self, sql_oper: str | None, py_oper: str | None, str_tmpl: str | Any = None
    ):
        self.__sql_oper = sql_oper
        self.__py_oper = py_oper
        self.__str_tmpl: Any[Any] = default_tmpl if not str_tmpl else str_tmpl

    def __str__(self):
        return self.__sql_oper

    # def format(self, **kwargs):
    #     return self.template.format(operator=self.sql, **kwargs)

    def format(self, column=None, *, value=0, min_value=0, max_value=0):
        if value and not min_value and not max_value:
            if callable(self.__str_tmpl):
                return self.__str_tmpl(column, self.__sql_oper, value)
        elif min_value and max_value:
            if callable(self.__str_tmpl):
                return self.__str_tmpl(column, self.__sql_oper, min_value, max_value)

    @classmethod
    def lt(cls):
        return cls("<", "<", default_tmpl)

    @classmethod
    def le(cls):
        return cls("<=", "<=", default_tmpl)

    @classmethod
    def eq(cls):
        return cls("=", "==", default_tmpl)

    @classmethod
    def ne(cls):
        return cls("!=", "!=", default_tmpl)

    @classmethod
    def gt(cls):
        return cls(">", ">", default_tmpl)

    @classmethod
    def ge(cls):
        return cls(">=", ">=", default_tmpl)

    @classmethod
    def like(cls):
        return cls("~~", None, default_tmpl)

    @classmethod
    def ilike(cls):
        return cls("~~*", None, default_tmpl)

    @classmethod
    def not_like(cls):
        return cls("!~~", None, default_tmpl)

    @classmethod
    def not_ilike(cls):
        return cls("!~~*", None, default_tmpl)

    @classmethod
    def between(cls):
        return cls(
            "BETWEEN", None, lambda c, o, mn_v, mx_v: f"{c} {o} {mn_v} AND {mx_v}"
        )

    @classmethod
    def in_(cls):
        return cls("=", "in", lambda c, o, v: f"{c} {o} any({v})")

    @classmethod
    def in__(cls):
        return cls("IN", "in", lambda c, o, v: f"{c} {o} ({v})")

    @classmethod
    def contains(cls):
        return cls("=", "in", lambda c, o, v: f"{v} {o} any({c})")

    @classmethod
    def is_(cls):
        return cls("IS", "is", default_tmpl)


class Column_:
    pass


class SQLComparison:
    def __init__(
        self,
        operator: str | SQLOperator,
        aggregate: str | Any,
        column: Any,
        value: int | Any = None,
        min_value: int | Any = None,
        max_value: int | Any = None,
    ):
        self.operator = operator
        self.format = operator.format
        self.aggregate = aggregate
        self._column = column
        self.value = value
        self.min_value = min_value
        self.max_value = max_value

    @property
    def column(self):
        if self.aggregate:
            return f"{self.aggregate}({self._column})"
        else:
            return str(self._column)

    def __str__(self):
        return self.format(
            column=self.column,
            value=self.value,
            min_value=self.min_value,
            max_value=self.max_value,
        )


class Column:
    __slots__ = (
        "data_type",
        "primary_key",
        "default",
        "nullable",
        "unique",
        "name",
        "index",
        "index_name",
        "foreign_key",
        "table",
        "aggregate",
    )

    def __init__(
        self,
        name,
        data_type=None,
        *,
        primary_key=False,
        default=None,
        nullable=False,
        unique=False,
        foreign_key=None,
        table=None,
        index=None,
        index_name=None,
    ):

        self.name = name

        if not isinstance(data_type, SQLType):
            raise TypeError("`data_type` must be of SQLType")

        self.data_type = data_type
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.index = index
        self.index_name = None

        if sum(map(bool, [primary_key, default is not None, unique])) > 1:
            raise SchemaError(
                "Only one of `default`, `primary_key`, or " "`unique` may be present"
            )

        if table and not isinstance(table, Table):
            raise SchemaError("`table` must be a `Table` object")

        self.table = table
        self.aggregate = None

        if foreign_key:
            if not isinstance(foreign_key, Column):
                raise SchemaError("`foreign_key` must be a `Column` object")

        self.foreign_key = foreign_key

    @property
    def full_name(self):
        return f"{self.table}.{self.name}" if self.table else self.name

    def __str__(self):
        if self.aggregate:
            return f"{self.aggregate} ({self.full_name})"
        else:
            return self.full_name

    def __lt__(self, value):
        return SQLComparison(SQLOperator.lt(), self.aggregate, self.full_name, value)

    def __le__(self, value):
        return SQLComparison(SQLOperator.le(), self.aggregate, self.full_name, value)

    def __eq__(self, value):
        return SQLComparison(SQLOperator.eq(), self.aggregate, self.full_name, value)

    def __ne__(self, value):
        return SQLComparison(SQLOperator.ne(), self.aggregate, self.full_name, value)

    def __gt__(self, value):
        return SQLComparison(SQLOperator.gt(), self.aggregate, self.full_name, value)

    def __ge__(self, value):
        return SQLComparison(SQLOperator.ge(), self.aggregate, self.full_name, value)

    def like(self, value):
        return SQLComparison(SQLOperator.like(), self.aggregate, self.full_name, value)

    def ilike(self, value):
        return SQLComparison(SQLOperator.ilike(), self.aggregate, self.full_name, value)

    def not_like(self, value):
        return SQLComparison(
            SQLOperator.not_like(), self.aggregate, self.full_name, value
        )

    def not_ilike(self, value):
        return SQLComparison(
            SQLOperator.not_ilike(), self.aggregate, self.full_name, value
        )

    def between(self, minvalue, maxvalue):
        return SQLComparison(
            SQLOperator.between(),
            self.aggregate,
            self.full_name,
            min_value=minvalue,
            max_value=maxvalue,
        )

    def in_(self, value):
        if isinstance(value, Column):
            return SQLComparison(
                SQLOperator.in__(), self.aggregate, self.full_name, value
            )

        return SQLComparison(SQLOperator.in_(), self.aggregate, self.full_name, value)

    def contains(self, value):  # *values
        # if (isinstance(v, Column) == True for v in values):
        if isinstance(value, Column) or isinstance(value, (int, str, bool)):
            return SQLComparison(
                SQLOperator.contains(), self.aggregate, self.full_name, value
            )

    @classmethod
    def from_dict(cls, data):
        name = data.pop("name")
        data_type = data.pop("data_type")
        data_type = SQLType.from_dict(data_type)
        return cls(name, data_type=data_type, **data)

    def to_sql(self):
        sql = []
        sql.extend([self.full_name, self.data_type.to_sql()])

        if self.default is not None:
            if isinstance(self.default, str) and isinstance(self.data_type, str):
                default = f"'{self.default}'"
            elif isinstance(self.default, bool):
                default = str(self.default).upper()
            elif isinstance(self.data_type, ArraySQL):
                default = f"{self.default}::{self.data_type.to_sql()}"
            else:
                default = f"{self.default}"
            sql.append(f"DEFAULT {default}")

        elif self.unique:
            sql.append("UNIQUE")

        if not self.nullable:
            sql.append("NOT NULL")

        if self.foreign_key:
            fkey_table, fkey_name = self.foreign_key.name.split(".", 1)
            sql.append(f"REFERENCES {fkey_table} ({fkey_name})")

        return " ".join(sql)

    @property
    def count(self):
        self.aggregate = "COUNT"
        return self

    @property
    def sum(self):
        self.aggregate = "SUM"
        return self

    @property
    def avg(self):
        self.aggregate = "AVG"
        return self

    @property
    def min(self):
        self.aggregate = "MIN"
        return self

    @property
    def max(self):
        self.aggregate = "MAX"
        return self

    async def set(self, value):
        if not self.table:
            return None
        data = dict(self.table.current_filter)  # type: ignore
        data[self.full_name] = value
        return await self.table.upsert(**data)  # type: ignore

    async def get(self, **filters):
        return await self.table.get(columns=self.name, **filters)  # type: ignore

    async def get_first(self, **filters):
        return await self.table.get_first(column=self.name, **filters)  # type: ignore


class PrimaryKeyColumn(Column):
    def __init__(
        self, name: str, big_int: bool = False, auto_increment: bool = False, **kwargs
    ):
        super().__init__(
            name,
            data_type=Integer(auto_increment=auto_increment),
            primary_key=True,
            **kwargs,
        )


class StringColumn(Column):
    def __init__(self, name=None, **kwargs):
        super().__init__(name, String(), **kwargs)


class IntColumn(Column):
    def __init__(self, name, big=False, small=False, **kwargs):

        super().__init__(name, Integer(big=big, small=small), **kwargs)

    @staticmethod
    def many(*cols: tuple[str, dict[Any, Any]]):
        """Return many IntColuumn's using a list of of arguments"""
        columns = []
        for col in cols:
            list_col = list(col)
            name = list_col[0]
            args = list_col[1:] if isinstance(list_col[1:], dict) else {}
            columns.append(IntColumn(name, *args))


class BoolColumn(Column):
    def __init__(self, name, **kwargs):
        super().__init__(name, Boolean(), **kwargs)


class DatetimeColumn(Column):
    def __init__(self, name, *, timezone=False, **kwargs):
        super().__init__(name, Datetime(timezone=timezone), **kwargs)


class DecimalColumn(Column):
    def __init__(self, name, *, precision=None, scale=None, **kwargs):
        super().__init__(name, Decimal(precision=precision, scale=scale), **kwargs)


class IntervalColumn(Column):
    def __init__(self, name, field=False, **kwargs):
        super().__init__(name, Interval(field), **kwargs)


class ListArguments:
    def __init__(self, args):
        self._args = args

    def __len__(self):
        return len(self._args)

    def __contains__(self, column):
        return SQLComparison(SQLOperator.in_(), None, column.full_name, self._args)


class TableAlter:
    __slots__ = ("table", "upgrade", "downgrade")

    def __init__(self, table, upgrade, downgrade):
        self.table = table
        self.upgrade = upgrade
        self.downgrade = downgrade

    def to_sql(self, *, downgrade=False):
        stmts = []
        base = f"ALTER TABLE {self.table.full_name}"
        modes = self.upgrade if not downgrade else self.downgrade

        for rename in modes.get("rename_columns", []):
            stmts.append(
                f"{base} RENAME COLUMN " f"{rename['before']} TO " f"{rename['after']};"
            )

        extnd_stmts = []
        for drop in modes.get("drop_columns", []):
            extnd_stmts.append(f"DROP COLUMN {drop['name']} RESTRICT")

        for alter in modes.get("alter_column_types", []):
            ext = f"ALTER COLUMN {alter['name']} " f"SET DATA TYPE {alter['type']}"

            using = alter.get("using")
            if using:
                ext += f" USING {using}"

            extnd_stmts.append(ext)

        for constraint in modes.get("alter_constrains", []):
            before = constraint["before"]
            after = constraint["after"]

            b_default = before.get("default")
            a_default = after.get("default")

            altr = f"ALTER COLUMN {constraint['name']}"

            if b_default is None and a_default is not None:
                extnd_stmts.append(f"{altr} SET DEFAULT {after['default']}")
            elif b_default is not None and a_default is None:
                extnd_stmts.append(f"{altr} DROP DEFAULT")

            b_null = before.get("nullable")
            a_null = after.get("nullable")
            if not b_null and a_null:
                extnd_stmts.append(f"{altr} DROP NOT NULL")
            elif b_null and not a_null:
                extnd_stmts.append(f"{altr} SET NOT NULL")

        for add in modes.get("added_columns", []):
            column = Column.from_dict(add)
            extnd_stmts.append(f"ADD COLUMN {column.to_sql()}")

        if extnd_stmts:
            stmts.append(f"{base} {', '.join(extnd_stmts)};")

        for drop in modes.get("dropped_indexes", []):
            stmts.append(f"DROP INDEX IF EXISTS {drop['index']}")

        for add in modes.get("added_indexes", []):
            stmts.append(
                f"CREATE INDEX IF NO EXISTS {add['index']}"
                f"ON {self.table.full_name} ({add['name']})"
            )


class Schema:
    __slots__ = ("name", "db")

    def __init__(self, db, name: str):
        self.db = db
        self.name = name

    def __str__(self):
        return self.name

    async def exists(self):
        schemata_table = self.database.table("information_schema.schemata")
        query = schemata_table.query("schema_name")
        result = await query.where(schema_name=self.name).get_value()
        return bool(result)

    async def drop(self, cascade=False):
        sql = "DROP SCHEMA $1"
        if cascade:
            sql += " CASCADE"
        return await self.database.execute_transaction(sql, self.name)

    def sql(self, skip_if_exists=True):
        if skip_if_exists:
            sql = "CREATE SCHEMA IF NOT EXISTS $1"
        else:
            sql = "CREATE SCHEMA $1"
        return (sql, self.name)

    async def create(self, skip_if_exists=True):
        sql, value = self.sql(skip_if_exists)
        await self.database.execute_transaction(sql, value)
        return self


class TableColumns:
    def __init__(self, table):
        self._table = table
        self._db = table.db

    def get_column(self, name):
        return Column(name, table=self._table)

    def get_columns(self, *names):
        return [Column(name, table=self._table) for name in names]

    async def info(self, *names):
        meta_table = Table("information_schema.columns", self._db)
        meta_table.query.where(TABLE_NAME=self._table.name)
        if names:
            meta_table.query.where(meta_table["COLUMN_NAME"].in_(names))

        return await meta_table.query.get()

    async def get_names(self):
        meta_table = Table("information_schema.columns", self._db)
        meta_table.query("column_name")
        meta_table.query.where(TABLE_NAME=self._table.name)
        return await meta_table.query.get_values()

    async def get_primaries(self):
        kcu = Table("information_schema.key_column_usage", self._db)
        query = kcu.query("column_name").where(
            table_name=self._table.name, constraint_name=f"{self._table.name}_pkey"
        )

        return await query.get_values()


class Table:
    __slots__ = (
        "name",
        "db",
        "schema",
        "columns",
        "new_columns",
        "query",
        "insert",
        "update",
        "where",
        "initial_data",
    )

    def __init__(self, name, db, *, schema=None):
        if "." in name and not schema:
            schema, name = name.split(".", 1)
            schema = Schema(db, schema)

        self.name = name
        if schema:
            if isinstance(schema, str):
                schema = Schema(db, schema)
        self.schema = schema
        self.db = db
        self.where = SQLConditions(parent=self)
        self.columns = TableColumns(table=self)
        self.new_columns = []
        self.initial_data = []
        self.query = Query(db, self)
        self.insert = Insert(db, self)
        self.update = Update(db, self)

    @property
    def full_name(self):
        return f"{self.schema}.{self.name}" if self.schema else self.name

    def __str__(self):
        return self.full_name

    def __hash__(self):
        return hash(str(self))

    def __getitem__(self, key):
        return self.columns.get_column(key)

    def __eq__(self, other):
        if isinstance(other, Table):
            return self.name == other.name
        return False

    def sql(self, *columns, primaries=None):
        """Generate SQL for creating the table."""
        sql = []
        # if self.schema:
        #     sql.append(str(self.schema.sql()))
        #     sql.append('\n')
        sql.append(f"CREATE TABLE {self.full_name} IF NOT EXISTS (")
        if not columns:
            if not self.new_columns:
                raise SchemaError("No columns for created table.")
            columns = self.new_columns
        sql.append(", ".join(col.to_sql for col in columns))
        if not primaries:
            primaries = [col.name for col in columns if col.primary_key]

        if primaries:
            if isinstance(primaries, str):
                sql.append(
                    f", CONSTRAINT {self.name}_pkey " f"PRIMARY KEY ({primaries})"
                )

            elif isinstance(primaries, (list, tuple, set)):
                sql.append(
                    f", CONSTRAINT {self.name}_pkey"
                    f" PRIMARY KEY ({', '.join(primaries)})"
                )

        sql.append(")")
        return "".join(sql)

    async def create(self, *columns, primaries=None):
        """Create table and return the object representing it."""
        # if self.schema:
        #     await self.schema.create()

        sql = f"CREATE TABLE {self.full_name} IF NOT EXISTS ("
        if not columns:
            if not self.new_columns:
                raise SchemaError("No columns for created table.")

            columns = self.new_columns

        sql += ", ".join(col.to_sql for col in columns)
        if not primaries:
            primaries = [col.name for col in columns if col.primary_key]

        if primaries:
            if isinstance(primaries, str):
                sql += f", CONSTRAINT {self.name}_pkey PRIMARY KEY ({primaries})"

            elif isinstance(primaries, (list, tuple, set)):
                sql += (
                    f", CONSTRAINT {self.name}_pkey"
                    f" PRIMARY KEY ({', '.join(primaries)})"
                )

        sql += ")"
        await self.database.execute_transaction(sql)
        if self.initial_data:
            await self.insert.rows(self.initial_data).commit(do_update=False)
        return self

    async def exists(self):
        """Create table and return the object representing it."""
        sql = f"SELECT to_regclass('{self.full_name}')"
        result = await self.database.execute_query(sql)
        return bool(list(result[0])[0])

    async def drop(self):
        """Drop table from database."""
        sql = "DROP TABLE $1"
        return await self.database.execute_transaction(sql, (self.full_name,))

    async def get_constraints(self):
        """Get column from table."""
        table = Table("information_schema.table_constraints", self.db)
        table.query("constrain_name").where(
            TABLE_NAME=table, CONSTRAINT_TYPE="PRIMARY KEY"
        )
        return await table.query.get_values()


class SQLConditions:
    def __init__(self, parent=None, allow_having=True):
        self.allow_having = allow_having
        self._parent = parent
        self.where_conditions = []
        self.having_conditions = []
        self._queued_conditions = []
        self.values = []
        self.add = self.add_having if allow_having else self.add_conditions
        self._count_token = 0

    def clear(self):
        self.where_conditions = []
        self.having_conditions = []
        self.values = []
        return self

    def sort_conditions(self, *conditions, allow_having=True):
        having_list = []
        where_list = []
        comps = {c for c in conditions if isinstance(c, SQLComparison)}
        not_comps = set(*conditions) - comps
        not_comps, comps = self.partition(
            lambda c: isinstance(c, SQLComparison), conditions
        )

        where, having = self.partition(lambda c: c.aggregate, comps)

        if not self.allow_having and having:
            raise SchemaError("'HAVING' cannot be in an update statement")
        if not allow_having and having:
            raise SchemaError("'HAVING' cannot be an 'OR' condition.")

        where_list.extend(where)
        having_list.extend(having)

        for c in not_comps:
            where_list.append(self.sort_conditions(*c)[0])

        if allow_having:
            return (tuple(where_list), tuple(having_list))

        return tuple(where_list)

    @staticmethod
    def process_dict_conditions(conditions):
        eq = SQLOperator.eq()
        c_list = [SQLComparison(eq, None, k, v) for k, v in conditions.items()]
        return c_list

    @property
    def _count(self):
        self._count_token += 1
        return self._count_token

    def submit_conditions(self, *conditions, having=False):
        if having:
            cond_list = self.having_conditions
        else:
            cond_list = self.where_conditions

        def make_string(*conditions):
            condition_strings = []
            for condition in conditions:
                if isinstance(condition, tuple):
                    c = make_string(*condition)
                    con_str = f"({' OR '.join(c)})"
                    condition_strings.append(con_str)
                    continue
                data = dict(column=condition.column)
                if condition.value is not None:
                    if isinstance(condition.value, Column):
                        data.update(value=str(condition.value))
                    else:
                        data.update(value=f"${self._count}")
                        self.values.append(condition.value)
                else:
                    data.update(minvalue=f"${self._count}")
                    self.values.append(condition.minvalue)
                    data.update(maxvalue=f"${self._count}")
                    self.values.append(condition.maxvalue)
                condition_strings.append(condition.format(**data))
            return condition_strings

        cond_list.extend(make_string(*conditions))

    def add_conditions(self):
        for conditions, kwarg_conditions in self._queued_conditions:
            if kwarg_conditions:
                k_conds = self.process_dict_conditions(kwarg_conditions)
                k_conds.extend(conditions)
                conditions = k_conds

            where, having = self.sort_conditions(*conditions)
            self.submit_conditions(*where)
            self.submit_conditions(*having, having=True)

        return self._parent

    def queue_conditions(self, *conditions, **kwargs_conditions):
        self._queued_conditions.append((conditions, kwargs_conditions))
        return self._parent

    def add_having(self, *conditions):
        self.having_conditions.extend(conditions)
        return self._parent

    def or_(self, *conditions, **kwarg_conditions):
        if kwarg_conditions:
            k_conds = self.process_dict_conditions(kwarg_conditions)
            k_conds.extend(conditions)
            conditions = tuple(k_conds)
        return self.queue_conditions(conditions)


class Query:
    """Builds a database query."""

    def __init__(self, db, *tables):
        self._db = db
        self._with = []
        self._select = ["*"]
        self._distinct = False
        self._group_by = []
        self._order_by = []
        self._sort = ""
        self._from = set()
        if tables:
            self.table(*tables)

        self._limit = None
        self._offset = None
        self._inner_join = None
        self._left_join = None
        self._using = None
        self.conditions = SQLConditions(parent=self)
        self.where = self.conditions.queue_conditions
        self.having = self.conditions.add_having

    def with_(self, *withs):
        for name, statement in withs:
            statement.conditions._count_token = self.conditions._count_token

            self._with.append([name, statement.sql(raw=True)])
            self.conditions.values.extend(statement.conditions.values)
            self.conditions._count_token += statement.conditions._count_token

        return self

    def select(self, *columns, distinct=False):
        self._select = []
        self._distinct = distinct

        for col in columns:
            if isinstance(col, Column):
                self._select.append(str(col))
                if not self._from and col.table:
                    self._from.add(col.table)

            elif isinstance(col, str):
                self._select.append(col)

        return self

    __call__ = select

    def distinct(self, distinct_select=True):
        self._distinct = distinct_select
        return self

    def table(self, *tables):
        self._from = set()
        for table in tables:
            if isinstance(table, Table):
                self._from.add(table)
            elif isinstance(table, str):
                self._from.add(Table(table, self._db))
            else:
                type_given = type(table).__name__
                raise SyntaxError(f"Unexpected data type encountered: {type_given}")

        return self

    def group_by(self, *columns):
        for col in columns:
            if isinstance(col, Column):
                self._group_by.append(col.full_name)
            elif isinstance(col, str):
                self._group_by.append(col)
        return self

    def order_by(self, *columns, asc: bool | None = None):
        if asc is False:
            sort = " DESC"
        if asc is True:
            sort = " ASC"
        if asc is None:
            sort = ""
        for col in columns:
            if isinstance(col, Column):
                self._order_by.append(f"{col.full_name}{sort}")  # type: ignore
            elif isinstance(col, str):
                self._order_by.append(f"{col}{sort}")  # type: ignore
        return self

    def limit(self, number=None):
        if not isinstance(number, (int, type(None))):
            raise TypeError("Method 'limit' only accepts an int argument.")
        self._limit = number
        return self

    def offset(self, number=None):
        if not isinstance(number, (int, type(None))):
            raise TypeError("Method 'offset' only accepts an int argument.")
        self._offset = number
        return self

    def inner_join(self, table, col):
        if not isinstance(col, str):
            raise TypeError("Method 'inner_join' only accepts a string argument.")

        self._inner_join = table
        self._using = col
        return self

    def left_join(self, table, *cols):
        if not isinstance(table, (Table, str)):
            raise TypeError("Argument 'table' must be of type 'str' or 'Table'")
        for col in cols:
            if not isinstance(col, (Column, str)):
                raise TypeError("Using columns must be of type 'str' or 'Column'")

        self._left_join = table
        self._using = cols
        return self

    def sql(self, delete=False, raw=False):
        sql = []
        if self._with:
            sql.append("WITH")
            sql.append(
                ", ".join(f"{name} AS ({statement})" for name, statement in self._with)
            )

        if delete:
            sql.append("DELETE")
        else:
            select_str = "SELECT DISTINCT" if self._distinct else "SELECT"
            if not self._select:
                sql.append(f"{select_str} *")
            else:
                select_names = [str(c) for c in self._select]
                sql.append(f"{select_str} {', '.join(select_names)}")

        table_names = [t.full_name for t in self._from]
        sql.append(f"FROM {', '.join(table_names)}")

        if self._left_join:
            sql.append(
                (
                    f"LEFT JOIN {self._left_join} " f"USING({', '.join(self._using)}) "
                )  # type: ignore
            )

        elif self._inner_join:
            sql.append((f"INNER JOIN {self._inner_join} " f"USING({self._using}) "))

        if self.conditions._queued_conditions:
            self.conditions.add_conditions()

        if self.conditions.where_conditions:
            con_sql = self.conditions.where_conditions
            sql.append(f"WHERE {' AND '.join(con_sql)}")
        if self._group_by:
            sql.append(f"GROUP BY {', '.join(self._group_by)}")
        if self.conditions.having_conditions:
            con_sql = self.conditions.having_conditions
            sql.append(f"HAVING {' AND '.join(con_sql)}")
        if self._order_by:
            sql.append(f"ORDER BY {', '.join(self._order_by)}")
        if self._limit:
            sql.append(f"LIMIT {self._limit}")
        if self._offset:
            sql.append(f"OFFSET {self._offset}")

        if not raw:
            return (f"{' '.join(sql)};", self.conditions.values)

        return f"{' '.join(sql)}"

    async def delete(self, **conditions):
        if conditions:
            self.conditions.add_conditions(**conditions)
        query, args = self.sql(delete=True)
        return await self._db.execute_query(query, *args)

    async def get(self):
        query, args = self.sql()
        return await self._db.execute_query(query, *args)

    async def get_one(self):
        if not self._limit:
            self.limit(2)
        data = await self.get()
        self.limit()
        if len(data) > 1:
            raise ResponseError("More than one result returned.")
        if not data:
            return None
        return data[0]

    async def get_first(self):
        old_limit = self._limit
        self.limit(1)
        data = await self.get()
        self.limit(old_limit)
        if not data:
            return None
        return data[0]

    async def get_value(self, *cols_selected):
        if cols_selected:
            self.select(*cols_selected)
        if len(self._select) == 1 or self._select == "*":
            data = await self.get_first()
            if not data:
                return None
            return next(data.values())
        else:
            raise QueryError("Query doesn't have a single column selected.")

    async def get_values(self):
        if len(self._select) == 1 or self._select == "*":
            data = await self.get()
            return [next(row.values()) for row in data]
        else:
            raise QueryError("Query doesn't have a single column selected.")


class Insert:
    """Insert data into database table."""

    def __init__(self, db, table=None):
        self._db = db
        self._from = None
        if table:
            self.table(table)
        self._data = []
        self._columns = None
        self._returning = None
        self._primaries = None

    def table(self, table):
        if isinstance(table, Table):
            self._from = table
        elif isinstance(table, str):
            self._from = Table(table, self._db)
        else:
            type_given = type(table).__name__
            raise SyntaxError(f"Unexpected data type encountered: {type_given}.")

        return self

    def returning(self, *columns):
        self._returning = columns
        return self

    def sql(self, do_update=None):
        """Build the SQL and sort data ready for db processing.
        Parameters:
        -----------
        do_update: :class:`bool`
            `None` is default, which raises a `UniqueViolationError` exception
            when the primary keys are found to be a duplicate.
            `True` allows it to update the existing data if found to exist
            already.
            `False` suppresses the exception and just does nothing when a
            duplicate is encountered.
        """

        # get columns
        cols = self._columns or set(chain.from_iterable(self._data))

        # ensure all data entries have no missing keys
        if not self._columns:
            for entry in self._data:
                entry.update((k, None) for k in cols - entry.keys())

        # order columns and build column indexes
        col_idx, cols = zip(*[(f"${i+1}", c) for i, c in enumerate(cols)])

        # sort all data entries into in same order of columns
        data = []
        for entry in self._data:
            entry_values = tuple(entry[d] for d in cols)
            data.append(entry_values)

        # build the insert statement
        col_str, idx_str = (", ".join(cols), ", ".join(col_idx))
        sql = f"INSERT INTO {self._from} ({col_str}) VALUES ({idx_str})"

        # handle conflict if required
        if do_update:
            const_str = ", ".join(self._primaries)  # type: ignore
            sql += f" ON CONFLICT ({const_str}) DO UPDATE SET "
            excluded = [f"{c} = excluded.{c}" for c in cols]
            sql += ", ".join(excluded)

        if do_update is False:
            const_str = ", ".join(self._primaries)  # type: ignore
            sql += f" ON CONFLICT ({const_str}) DO NOTHING"

        # add the returning statement if specified
        if self._returning:
            sql += f" RETURNING {', '.join(self._returning)}"

        return (sql, tuple(data))

    def sql_test(self, do_update=None):
        """SQL test output"""
        sql, data = self.sql(do_update)
        data_str = ",\n".join(str(d) for d in data)
        msg = f"**SQL**```sql\n{sql}\n```\n**Data**```py\n{data_str}\n```"
        return msg

    async def commit(self, do_update=None):
        """Commit the data in the current insert session to the database.
        Parameters:
        -----------
        do_update: :class:`bool`
            `None` is default, which raises a `UniqueViolationError` exception
            when the primary keys are found to be a duplicate.
            `True` allows it to update the existing data if found to exist
            already.
            `False` suppresses the exception and just does nothing when a
            duplicate is encountered.
        """
        if not self._from:
            raise SchemaError("A table must be declared.")

        if do_update is not None and not self._primaries:
            self._primaries = await self._from.columns.get_primaries()

        sql, data = self.sql(do_update)
        return await self._db.execute_transaction(sql, *data)

    def set_columns(self, *columns):
        """Declares the columns for positional arg data entry."""
        if not columns:
            return self._columns

        if self._data:
            raise SchemaError("Columns must be declared before data has been added.")

        self._columns = columns
        return self

    def primaries(self, *primaries):
        if not primaries:
            return self._primaries

        self._primaries = primaries
        return self

    def row(self, *values, **dict_values):
        """Add row data to insert.
        Pass data with column name as keyword and the data as their values.
        If insert column names has been set with ``insert.columns()``,
        positional args may be passed in the same order of declaration.
        """

        if values and dict_values:
            raise SyntaxError(
                "Unable to mix positional args and kwargs when adding row "
                "data. Use only positional args if columns are set or all "
                "columns will be specified. Use only kwargs if adding row "
                "data to specify relevant columns."
            )

        if values and not self._columns:
            raise SyntaxError(
                "Columns must be declared before being able to use "
                "positional args for this method."
            )

        if values:
            dict_values = dict(zip_longest(self._columns, values))  # type: ignore
            if None in dict_values:
                raise SyntaxError(
                    "Too many values given "
                    f"({len(values)}/{len(self._columns)})"  # type: ignore
                )

        if dict_values:
            self._data.append(dict_values)

        return self

    def rows(self, data_iterable):
        """Add row data in bulk to insert."""
        if not hasattr(data_iterable, "__iter__"):
            raise SyntaxError(
                "Non-iterable encountered in rows method. Can only accept "
                "an iterable of data for adding row data in bulk."
            )

        for row in data_iterable:
            if isinstance(row, dict):
                self.row(**row)
            else:
                self.row(*row)

        return self

    def __call__(self, *args, **kwargs):
        if args and kwargs:
            raise SyntaxError(
                "Unable to mix positional args and kwargs in base call "
                "for Insert. Use only positional args if setting the columns "
                "or use kwargs if adding a row as a shortcut."
            )

        if args:
            self.set_columns(*args)
        if kwargs:
            self.row(**kwargs)

        return self


class Update:
    """Update data in a database table."""

    def __init__(self, db, table=None):
        self._db = db
        self._from = None
        if table:
            self.table(table)
        self._data = []
        self._columns = None
        self._returning = None
        self.conditions = SQLConditions(parent=self)
        self.where = self.conditions.add_conditions

    def table(self, table):
        if isinstance(table, Table):
            self._from = table
        elif isinstance(table, str):
            self._from = Table(table, self._db)
        else:
            type_given = type(table).__name__
            raise SyntaxError(f"Unexpected data type encountered: {type_given}.")

        return self

    def returning(self, *columns):
        self._returning = columns
        return self

    def sql(self, allow_no_condition=False):
        """Build the SQL and sort data ready for db processing."""

        # get columns
        cols = self._columns or set(chain.from_iterable(self._data))

        # ensure all data entries have no missing keys
        if not self._columns:
            for entry in self._data:
                entry.update((k, None) for k in cols - entry.keys())

        # order columns and build column indexes
        offset = 1
        if self.conditions.where_conditions:
            offset = self.conditions._count_token + 1
        col_idx, cols = zip(*[(f"${i+offset}", c) for i, c in enumerate(cols)])

        # build conditions
        if self.conditions.where_conditions:
            conditions = self.conditions.where_conditions
            cond_sql = f"WHERE {' AND '.join(conditions)}"
            cond_values = self.conditions.values
        else:
            if not allow_no_condition:
                raise SchemaError(
                    "No condition provided for Update. If this is "
                    "intentional, use the 'allow_no_condition' kwarg."
                )

            else:
                cond_values = []

        # sort all data entries into in same order of columns
        data = []
        for entry in self._data:
            entry_values = tuple(cond_values + [entry[d] for d in cols])
            data.append(entry_values)

        # build the insert statement
        col_str, idx_str = (", ".join(cols), ", ".join(col_idx))
        if len(cols) > 1:
            sql = [f"UPDATE {self._from} SET ({col_str}) = ({idx_str})"]
        else:
            sql = [f"UPDATE {self._from} SET {col_str} = {idx_str}"]

        # add conditions
        if self.conditions.where_conditions:
            sql.append(cond_sql)  # type: ignore

        # add the returning statement if specified
        if self._returning:
            sql.append(f"RETURNING {', '.join(self._returning)}")

        return (" ".join(sql), tuple(data))

    def sql_test(self, allow_no_condition=False):
        """SQL test output"""
        sql, data = self.sql(allow_no_condition)
        data_str = "\n".join(str(d) for d in data)
        msg = f" ```\n**SQL**```sql\n{sql}\n```\n**Data**```py\n{data_str}\n"
        return msg

    async def commit(self, allow_no_condition=False):
        """Commit the data in the current update session to the database."""
        sql, data = self.sql(allow_no_condition)
        await self._db.execute_transaction(sql, *data)

    def columns(self, *columns):
        if not columns:
            return self._columns
        if self._data:
            raise SchemaError("Columns must be declared before values are defined.")

        self._columns = columns
        return self

    def values(self, *values, **dict_values):
        """Add values to update rows that match the update conditions.
        Pass data with column name as keyword and the data as their values.
        If update column names has been set with ``update.columns()``,
        positional args may be passed in the same order of declaration.
        """

        if values and dict_values:
            raise SyntaxError(
                "Unable to mix positional args and kwargs when adding row "
                "data. Use only positional args if columns are set or all "
                "columns will be specified. Use only kwargs if adding row "
                "data to specify relevant columns."
            )

        if values and not self._columns:
            raise SyntaxError(
                "Columns must be declared before being able to use "
                "positional args for this method."
            )

        if values:
            dict_values = dict(zip_longest(self._columns, values))  # type: ignore
            if None in dict_values:
                raise SyntaxError(
                    "Too many values given "
                    f"({len(values)}/{len(self._columns)})"  # type: ignore
                )

        if dict_values:
            self._data.append(dict_values)

        return self

    def __call__(self, *args, **kwargs):
        if args and kwargs:
            raise SyntaxError(
                "Unable to mix positional args and kwargs in base call "
                "for Update. Use only positional args if setting the columns "
                "or use kwargs if adding a row as a shortcut."
            )

        if args:
            self.columns(*args)
        if kwargs:
            self.values(**kwargs)

        return self
