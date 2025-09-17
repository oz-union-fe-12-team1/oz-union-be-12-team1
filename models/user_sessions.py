from tortoise import fields
from tortoise.models import Model


class UserSession(Model):
    id = fields.BigIntField(pk=True)  # BIGSERIAL PRIMARY KEY

    user = fields.ForeignKeyField(
        "models.User",
        related_name="sessions",
        on_delete=fields.CASCADE
    )  # user_id: BIGINT NOT NULL, FK(users.id)

    token_jti = fields.CharField(max_length=64, unique=True, null=False)  # VARCHAR(64) UNIQUE, NOT NULL
    ip_address = fields.CharField(max_length=45, null=True)  # INET (IPv4/IPv6 지원)
    user_agent = fields.TextField(null=True)  # TEXT

    is_active = fields.BooleanField(default=True)  # BOOLEAN NOT NULL, DEFAULT TRUE
    expires_at = fields.DatetimeField(null=False)  # TIMESTAMPTZ NOT NULL

    created_at = fields.DatetimeField(auto_now_add=True)  # TIMESTAMPTZ NOT NULL, DEFAULT now()
    last_activity_at = fields.DatetimeField(null=True)  # TIMESTAMPTZ

    class Meta:
        table = "user_sessions"