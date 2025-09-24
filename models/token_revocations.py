from tortoise import fields, ForeignKeyFieldInstance
from tortoise.models import Model

from models.user import User


class TokenRevocation(Model):
    id = fields.BigIntField(pk=True)

    user: ForeignKeyFieldInstance[User] = fields.ForeignKeyField(
        "models.User",
        related_name="revoked_tokens",
        on_delete=fields.CASCADE,
        null=False
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
