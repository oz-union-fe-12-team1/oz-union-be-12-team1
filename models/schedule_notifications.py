from tortoise import fields
from tortoise.models import Model
import enum


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class ScheduleNotification(Model):
    id = fields.BigIntField(pk=True)  # BIGSERIAL PRIMARY KEY

    schedule = fields.ForeignKeyField(
        "models.Schedule",
        related_name="notifications",
        on_delete=fields.CASCADE
    )  # schedule_id: BIGINT NOT NULL, FK(schedules.id)
    
    user = fields.ForeignKeyField(
        "models.User",
        related_name="schedule_notifications",
        on_delete=fields.CASCADE
    )  # user_id: BIGINT NOT NULL, FK(users.id)
    
    push_subscription = fields.ForeignKeyField(
        "models.PushSubscription",
        related_name="notifications",
        null=True,
        on_delete=fields.SET_NULL
    )  # push_subscription_id: BIGINT FK(push_subscriptions.id)
    
    notification_time = fields.DatetimeField(null=False)  # TIMESTAMPTZ NOT NULL - 알림 시간
    notification_type = fields.CharField(max_length=32, null=True)  # VARCHAR(32) - 알림 유형
    channel = fields.CharField(max_length=32, null=True)  # VARCHAR(32) - 알림 채널
    
    status = fields.CharEnumField(
        enum_type=NotificationStatus,
        default=NotificationStatus.pending
    )  # VARCHAR(32) - 알림 상태
    
    onesignal_id = fields.CharField(max_length=128, null=True)  # VARCHAR(128) - OneSignal 알림 ID
    sent_at = fields.DatetimeField(null=True)  # TIMESTAMPTZ - 발송 시각
    error_message = fields.TextField(null=True)  # TEXT - 오류 메시지
    created_at = fields.DatetimeField(auto_now_add=True)  # TIMESTAMPTZ NOT NULL, DEFAULT now()

    class Meta:
        table = "schedule_notifications"