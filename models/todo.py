from tortoise import fields
from tortoise.models import Model
from datetime import datetime
from typing import Optional


class Todo(Model):
    id: int = fields.BigIntField(pk=True)  # SERIAL → BigIntField

    user: "User" = fields.ForeignKeyField(
        "models.User",
        related_name="todos",
        on_delete=fields.CASCADE,
    )

    schedule: Optional["Schedule"] = fields.ForeignKeyField(
        "models.Schedule",
        related_name="todos",
        null=True,
        on_delete=fields.SET_NULL,
    )

    title: str = fields.CharField(max_length=255, null=False)
    description: Optional[str] = fields.TextField(null=True)

    is_completed: bool = fields.BooleanField(default=False)

    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)
    deleted_at: Optional[datetime] = fields.DatetimeField(null=True)
    # 소프트 딜리트 (삭제 시간 기록 → 복구 가능)

    class Meta:
        table = "todos"
