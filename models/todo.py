from tortoise import fields
from tortoise.models import Model


class Todo(Model):
    id = fields.BigIntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="todos",
        on_delete=fields.CASCADE,
    )

    schedule = fields.ForeignKeyField(
        "models.Schedule",
        related_name="todos",
        null=True,
        on_delete=fields.SET_NULL,
    )

    title = fields.CharField(max_length=255, null=False)
    description = fields.TextField(null=True)

    is_completed = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        table = "todos"
