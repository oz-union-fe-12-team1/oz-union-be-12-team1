from typing import Optional, TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from .users import users  # type: ignore


class TokenRevocations(Model):
    id = fields.BigIntField(pk=True)
    jti = fields.CharField(max_length=255, unique=True, null=False, index=True)
    user: Optional["users"] = fields.ForeignKeyField(
        "models.users", related_name="token_revocations", null=True, on_delete=fields.CASCADE
    )
    reason = fields.CharField(max_length=100, null=True)
    revoked_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField(null=False)

    class Meta:
        table = "token_revocations"
        ordering = ["-revoked_at"]

    def str(self):
        return f"TokenRevocations(id={self.id}, user={self.user_id}, jti={self.jti})"
