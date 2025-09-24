from __future__ import annotations  # 🔑 forward reference
from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:  # mypy 전용 (런타임에는 영향 없음)
    from models.user import User
    from models.schedules import Schedule


class Todo(Model):
    id = fields.BigIntField(pk=True)

    user: "User" = fields.ForeignKeyField(   # 🔑 타입힌트 추가
        "models.User",
        related_name="todos",
        on_delete=fields.CASCADE,
    )
    # FK → 사용자

    schedule: "Schedule" | None = fields.ForeignKeyField(  # 🔑 타입힌트 추가
        "models.Schedule",
        related_name="todos",
        null=True,
        on_delete=fields.SET_NULL,
    )
    # FK → 일정 (선택)

    title: str = fields.CharField(max_length=255, null=False)
    description: str | None = fields.TextField(null=True)

    is_completed: bool = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)  # ✅ Soft delete

    class Meta:
        table = "todos"
