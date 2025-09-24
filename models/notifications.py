from typing import TYPE_CHECKING, Optional
from tortoise import fields
from tortoise.models import Model
from datetime import datetime

if TYPE_CHECKING:
    from models.user import User
    from models.schedules import Schedule
    from models.todo import Todo


class Notification(Model):
    id: int = fields.BigIntField(pk=True)  # SERIAL → BigIntField

    user: "User" = fields.ForeignKeyField(
        "models.User",
        related_name="notifications",
        on_delete=fields.CASCADE,
        null=False,
    )
    # FK → 알림 수신 사용자

    schedule: Optional["Schedule"] = fields.ForeignKeyField(
        "models.Schedule",
        related_name="notifications",
        null=True,
        on_delete=fields.SET_NULL,
    )
    # FK → 관련 일정 (NULL 가능)

    todo: Optional["Todo"] = fields.ForeignKeyField(
        "models.Todo",
        related_name="notifications",
        null=True,
        on_delete=fields.SET_NULL,
    )
    # FK → 관련 할 일 (NULL 가능)

    message: str = fields.CharField(max_length=255, null=False)
    notify_at: Optional[datetime] = fields.DatetimeField(null=True)
    is_read: bool = fields.BooleanField(default=False)

    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notifications"
