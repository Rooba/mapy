from asyncpg import PostgresError


class SchemaError(PostgresError):
    ...


class ResponseError(PostgresError):
    ...


class QueryError(PostgresError):
    ...
