import enum
from tortoise import fields
from tortoise.models import Model


class Period(str, enum.Enum):
    daily = "daily"
    monthly = "monthly"


class AdminUsageLog(Model):
    id = fields.BigIntField(pk=True)

    period = fields.CharEnumField(
        enum_type=Period,
        null=False
    )

    date = fields.DateField(null=True)

    user_total = fields.IntField(null=True)
    active_user = fields.IntField(null=True)
    new_user = fields.IntField(null=True)

    weather_call = fields.IntField(null=True)
    ai_call = fields.IntField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "admin_usage_logs"