from __future__ import annotations  # 🔑 forward reference
from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model
from tortoise.fields import ForeignKeyRelation, ReverseRelation  # ✅ 타입힌트 전용

if TYPE_CHECKING:  # mypy 전용
    from models.user import User
    from models.todo import Todo
    from models.notifications import Notification


class Schedule(Model):
    id = fields.BigIntField(pk=True)

    user: ForeignKeyRelation["User"] = fields.ForeignKeyField(  # ✅ FK 타입 안정
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

    # ✅ 역참조 관계 (mypy 친화적)
    todos: ReverseRelation["Todo"]
    notifications: ReverseRelation["Notification"]

    class Meta:
        table = "schedules"
        indexes = (("user_id", "start_time"),)
