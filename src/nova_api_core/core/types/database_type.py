from enum import Enum


class DatabaseType(str, Enum):
    SQLALCHEMY = "sqlalchemy"
    MONGODB = "mongodb"
    NONE = "none"


class SQLEngineType(str, Enum):
    POSTGRES = "postgresql+asyncpg"
    MYSQL = "mysql+aiomysql"
    SQLITE = "sqlite+aiosqlite"
