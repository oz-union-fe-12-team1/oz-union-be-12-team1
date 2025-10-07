from typing import Optional

from tortoise import fields, ForeignKeyFieldInstance
from tortoise.models import Model

from models.schedules import Schedule
from models.user import User


class Todo(Model):
    id = fields.BigIntField(pk=True)  # SERIAL → BigIntField

    user: ForeignKeyFieldInstance[User] = fields.ForeignKeyField(
        "models.User",
        related_name="todos",
        on_delete=fields.CASCADE
    )

    title = fields.CharField(max_length=255, null=False)
    description = fields.TextField(null=True)

    is_completed = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    deleted_at = fields.DatetimeField(null=True)
    #소프트 딜리트 (삭제한 시간 저장, 이렇게 해야 복구를 할 수가 있음

    class Meta:
        table = "todos"
