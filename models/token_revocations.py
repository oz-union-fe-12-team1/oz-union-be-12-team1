from __future__ import annotations  # 🔑 forward reference
from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model
from tortoise.fields import ForeignKeyRelation  # ✅ 타입힌트 전용

if TYPE_CHECKING:  # mypy 전용 (런타임 영향 없음)
    from models.user import User


class TokenRevocation(Model):
    id = fields.BigIntField(pk=True)

    user: ForeignKeyRelation["User"] = fields.ForeignKeyField(  # ✅ 타입 안정
        "models.User",
        related_name="revoked_tokens",
        on_delete=fields.CASCADE,
        null=False,
    )
