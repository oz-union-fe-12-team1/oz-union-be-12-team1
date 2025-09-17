from tortoise import fields
from tortoise.models import Model


class PushSubscription(Model):
    id = fields.BigIntField(pk=True)  # BIGSERIAL PRIMARY KEY
    
    user = fields.ForeignKeyField(
        "models.User",
        related_name="push_subscriptions",
        on_delete=fields.CASCADE
    )  # user_id: BIGINT NOT NULL, FK(users.id)
    
    platform = fields.CharField(max_length=32, null=False)  # VARCHAR(32) NOT NULL - 플랫폼 (Web)
    device_token = fields.CharField(max_length=255, null=True)  # VARCHAR(255) - 디바이스 토큰
    onesignal_player_id = fields.CharField(max_length=255, unique=True, null=True)  # VARCHAR(255) UNIQUE - OneSignal 플레이어 ID
    device_info = fields.JSONField(default=dict)  # JSONB DEFAULT '{}' - 디바이스 정보
    
    is_active = fields.BooleanField(default=True)  # BOOLEAN NOT NULL, DEFAULT TRUE - 활성 상태
    last_used_at = fields.DatetimeField(null=True)  # TIMESTAMPTZ - 마지막 사용 시각
    created_at = fields.DatetimeField(auto_now_add=True)  # TIMESTAMPTZ NOT NULL, DEFAULT now()

    class Meta:
        table = "push_subscriptions"