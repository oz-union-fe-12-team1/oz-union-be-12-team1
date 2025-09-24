from __future__ import annotations
from tortoise import fields
from tortoise.models import Model
from typing import Optional
from datetime import datetime


class TokenRevocation(Model):
    id: int = fields.BigIntField(pk=True)

    user: "User" = fields.ForeignKeyField(
        "models.User",
        related_name="revoked_tokens",
        on_delete=fields.CASCADE,
        null=False,
    )
    # FK → 사용자

    jti: str = fields.CharField(max_length=128, unique=True, null=False)
    # 토큰 고유 ID

    reason: Optional[str] = fields.CharField(max_length=200, null=True)
    # 블랙리스트 사유 (선택)

    revoked_at: datetime = fields.DatetimeField(auto_now_add=True)
    # 블랙리스트 등록 시각

    expires_at: Optional[datetime] = fields.DatetimeField(null=True)
    # 토큰 만료 시각

    class Meta:
        table = "token_revocations"
        indexes = (("user_id", "jti"),)
