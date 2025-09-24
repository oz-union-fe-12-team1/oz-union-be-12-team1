from __future__ import annotations  # 🔑 forward reference
from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:  # mypy 전용 (런타임 영향 없음)
    from models.user import User


class TokenRevocation(Model):
    id = fields.BigIntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="revoked_tokens",
        on_delete=fields.CASCADE,
        null=False,
    )
    # FK → 사용자

    jti = fields.CharField(max_length=128, unique=True, null=False)
    # 토큰 고유 ID

    reason = fields.CharField(max_length=200, null=True)
    # 블랙리스트 사유 (선택)

    revoked_at = fields.DatetimeField(auto_now_add=True)
    # 블랙리스트 등록 시각

    expires_at = fields.DatetimeField(null=True)
    # 토큰 만료 시각

    class Meta:
        table = "token_revocations"
        indexes = (("user_id", "jti"),)
