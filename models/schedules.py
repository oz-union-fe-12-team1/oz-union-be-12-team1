from typing import TYPE_CHECKING, Optional, List
from tortoise import fields
from tortoise.models import Model
from datetime import datetime

if TYPE_CHECKING:
    from models.user import User
    from models.todo import Todo
    from models.notifications import Notification


class Schedule(Model):
    id: int = fields.BigIntField(pk=True)

    user: "User" = fields.ForeignKeyField(
        "models.User",
        related_name="schedules",
        on_delete=fields.CASCADE,
    )

    title: str = fields.CharField(max_length=255, null=False)
    description: Optional[str] = fields.TextField(null=True)

    start_time: datetime = fields.DatetimeField(null=False)
    end_time: datetime = fields.DatetimeField(null=False)
    all_day: bool = fields.BooleanField(default=False)
    location: Optional[str] = fields.CharField(max_length=255, null=True)

    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)

    # 관계 설정
    todos: fields.ReverseRelation["Todo"]
    notifications: fields.ReverseRelation["Notification"]

    class Meta:
        table = "schedules"
        indexes = (("user_id", "start_time"),)
