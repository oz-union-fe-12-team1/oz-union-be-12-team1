from tortoise import Tortoise
import os


def _build_database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres") 
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "postgres")
    
    return f"postgres://{user}:{password}@{host}:{port}/{dbname}"


TORTOISE_ORM = {
    "connections": {
        "default": _build_database_url(),
    },
    "apps": {
        "models": {
            "models": [
                "models.user",
                "models.user_settings",
                "models.user_sessions", 
                "models.schedules",
                "models.todo",
                "models.notifications",
                "models.api_usage_logs",
                "models.admin_usage_logs",
                "models.ai_conversations",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    }
}


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)


async def close_db():
    await Tortoise.close_connections()