from tortoise import Tortoise
from core.config import settings


TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
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
                "aerich.models",  #  마이그레이션 관리
            ],
            "default_connection": "default",
        },
    },
}


async def init_db(generate_schemas: bool = False):
    """
    데이터베이스 초기화
    :param generate_schemas: True이면 스키마를 자동 생성 (개발용)
    """
    await Tortoise.init(config=TORTOISE_ORM)

    if generate_schemas:
        await Tortoise.generate_schemas()


async def close_db():
    """DB 연결 종료"""
    await Tortoise.close_connections()
