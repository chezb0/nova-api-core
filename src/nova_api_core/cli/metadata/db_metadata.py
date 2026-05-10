from nova_api_core.core.types.database_type import DatabaseType

DB_METADATA = {
    DatabaseType.SQLALCHEMY: {
        "manager_import": "from nova_api_core.infra.db.sqlalchemy.database_manager import SQLAlchemyDatabaseManager",
        "config_fields": {
            "DB_ENGINE": "str",
            "DB_HOST": "str",
            "DB_PORT": "int",
            "DB_USER": "str",
            "DB_PASSWORD": "str",
            "DB_NAME": "str",
            "DB_MAX_RETRIES": "int",
            "DB_RETRY_DELAY": "float",
        },
        "env_defaults": {
            "DB_ENGINE": "mysql+aiomysql # or postgresql+asyncpg if your database is postgresql",
            "DB_HOST": "localhost",
            "DB_PORT": "3306",
            "DB_USER": "root",
            "DB_PASSWORD": "password2301",
            "DB_NAME": "nova_db",
            "DB_MAX_RETRIES": "3",
            "DB_RETRY_DELAY": "1.0",
        },
    },
    DatabaseType.MONGODB: {
        "manager_import": "from nova_api_core.infra.db.mongo.mongo_database_manager import MongoDatabaseManager",
        "config_fields": {
            "DB_HOST": "str",
            "DB_PORT": "int",
            "DB_USER": "str",
            "DB_PASSWORD": "str",
            "DB_NAME": "str",
            "DB_MAX_RETRIES": "int",
            "DB_RETRY_DELAY": "float",
        },
        "env_defaults": {
            "DB_HOST": "localhost",
            "DB_PORT": "27017",
            "DB_USER": "admin",
            "DB_PASSWORD": "password",
            "DB_NAME": "nova_db",
            "DB_MAX_RETRIES": "3",
            "DB_RETRY_DELAY": "1.0",
        },
    },
    DatabaseType.NONE: {"manager_import": "", "config_fields": {}, "env_defaults": {}},
}

BOOTSTRAP_DEFAULTS = {
    "APP_NAME": "NovaProject",
    "APP_VERSION": "0.1.0",
    "ENV": "dev",
    "LOG_LEVEL": "DEBUG",
    "LOG_OUTPUT": "CONSOLE",
}
