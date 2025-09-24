from tortoise import fields
from tortoise.models import Model


class TokenRevocation(Model):
    id = fields.BigIntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="revoked_tokens",
        on_delete=fields.CASCADE,
        null=False,
    )

    jti = fields.CharField(max_length=128, unique=True, null=False)
    reason = fields.CharField(max_length=200, null=True)

    revoked_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField(null=True)

    class Meta:
        table = "token_revocations"
        indexes = (("user_id", "jti"),)
