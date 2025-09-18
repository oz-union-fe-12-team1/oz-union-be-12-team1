from tortoise import fields
from tortoise.models import Model


class Schedule(Model):
    id = fields.BigIntField(pk=True)  # SERIAL → BigIntField

    user = fields.ForeignKeyField(
        "models.User",
        related_name="schedules",
        on_delete=fields.CASCADE
    )

    title = fields.CharField(max_length=255, null=False)
    description = fields.TextField(null=True)

    start_time = fields.DatetimeField(null=False)
    end_time = fields.DatetimeField(null=False)

    all_day = fields.BooleanField(default=False)
    location = fields.CharField(max_length=255, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Soft Delete (복구 가능)
    #deleted_at = fields.DatetimeField(null=True)

    # 역참조 (문자열 참조만으로 충분)
    todos: fields.ReverseRelation["Todo"]
    notifications: fields.ReverseRelation["Notification"]

    class Meta:
        table = "schedules"
