from tortoise import fields
from tortoise.models import Model


class UserSession(Model):
    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="sessions",
        on_delete=fields.CASCADE
    )

    token_jti = fields.CharField(max_length=255, unique=True, null=False)  # JWT 고유 ID
    device_info = fields.JSONField(null=True)
    ip_address = fields.CharField(max_length=45, null=True)  # IPv4/IPv6 모두 대응
    user_agent = fields.TextField(null=True)

    is_active = fields.BooleanField(default=True)
    expires_at = fields.DatetimeField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    last_activity_at = fields.DatetimeField(null=True)

    class Meta:
        table = "user_sessions"