from __future__ import annotations  # 🔑 forward reference
from typing import TYPE_CHECKING
from datetime import datetime
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:  # mypy 전용
    from models.user import User
    from models.schedule import Schedule
    from models.todo import Todo


class Notification(Model):
    id = fields.BigIntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="notifications",
        on_delete=fields.CASCADE,
        null=False,
    )
    # FK → 알림 수신 사용자

    schedule = fields.ForeignKeyField(
        "models.Schedule",
        related_name="notifications",
        null=True,
        on_delete=fields.SET_NULL,
    )
    # FK → 관련 일정 (NULL 가능)

    todo = fields.ForeignKeyField(
        "models.Todo",
        related_name="notifications",
        null=True,
        on_delete=fields.SET_NULL,
    )
    # FK → 관련 할 일 (NULL 가능)

    message = fields.CharField(max_length=255, null=False)
    # 알림 메시지

    notify_at = fields.DatetimeField(null=True)
    # 발송 예정 시간 (NULL → 즉시 발송 또는 인앱 전용)

    is_read = fields.BooleanField(default=False)
    # 읽음 여부

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notifications"
