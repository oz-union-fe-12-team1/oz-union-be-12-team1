import os
from tortoise import Tortoise

def _build_database_url():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    dbname = os.getenv("POSTGRES_DB", "postgres")
    port = os.getenv("DB_PORT", "5432")

    # 환경에 따라 host 달라지게 처리
    host = os.getenv("DB_HOST", "localhost")

    return f"postgres://{user}:{password}@{host}:{port}/{dbname}"

TORTOISE_ORM = {
    "connections": {"default": _build_database_url()},
    "apps": {
        "models": {
            "models": [
                "models.user",
                "models.schedules",
                "models.todos",
                "models.notifications",
                "models.inquiries",
                "models.token_revocations",
                "models.user_locations",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}

async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
