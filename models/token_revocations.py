from tortoise import fields
from tortoise.models import Model


class TokenRevocation(Model):
    id = fields.BigIntField(pk=True)
    jti = fields.CharField(max_length=255, unique=True, null=False)
    user = fields.ForeignKeyField("models.User", related_name="token_revocations", null=True, on_delete=fields.SET_NULL)
    reason = fields.CharField(max_length=100, null=True)
    revoked_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField(null=False)

    class Meta:
        table = "token_revocations"

    def __str__(self):
        return f"TokenRevocation(id={self.id}, user_id={self.user_id}, reason={self.reason})"

