from tortoise import fields
from tortoise.models import Model


class APIUsageLog(Model):
    id = fields.BigIntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="api_usage_logs",
        null=True,                # 시스템 호출은 NULL 가능
        on_delete=fields.SET_NULL
    )

    schedules_count = fields.IntField(null=True)
    todos_completed = fields.IntField(null=True)
    todos_pending = fields.IntField(null=True)

    usage_date = fields.DateField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "api_usage_logs"