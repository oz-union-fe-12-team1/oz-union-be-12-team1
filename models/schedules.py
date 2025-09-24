from __future__ import annotations  # 🔑 forward reference
from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:  # mypy 전용
    from models.user import User
    from models.todo import Todo
    from models.notifications import Notification


class Schedule(Model):
    id = fields.BigIntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="schedules",
        on_delete=fields.CASCADE,
    )
    # FK → 사용자

    title = fields.CharField(max_length=255, null=False)
    description = fields.TextField(null=True)

    start_time = fields.DatetimeField(null=False)
    end_time = fields.DatetimeField(null=False)
    all_day = fields.BooleanField(default=False)
    location = fields.CharField(max_length=255, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Reverse 관계 (여기만 타입 주석 허용)
    todos: fields.ReverseRelation["Todo"]
    notifications: fields.ReverseRelation["Notification"]

    class Meta:
        table = "schedules"
        indexes = (("user_id", "start_time"),)
