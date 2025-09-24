from tortoise import fields
from tortoise.models import Model


class Todo(Model):
    id = fields.BigIntField(pk=True)  # SERIAL → BigIntField

    user = fields.ForeignKeyField(
        "models.User",
        related_name="todos",
        on_delete=fields.CASCADE
    )
    schedule = fields.ForeignKeyField(
        "models.Schedule",
        related_name="todos",
        null=True,
        on_delete=fields.SET_NULL
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
