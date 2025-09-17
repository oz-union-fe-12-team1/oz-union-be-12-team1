from tortoise import fields
from tortoise.models import Model


class Notification(Model):
    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="notifications",
        on_delete=fields.CASCADE
    )

    schedule = fields.ForeignKeyField(
        "models.Schedule",
        related_name="notifications",
        null=True,
        on_delete=fields.SET_NULL
    )

    todo = fields.ForeignKeyField(
        "models.Todo",
        related_name="notifications",
        null=True,
        on_delete=fields.SET_NULL
    )

    message = fields.CharField(max_length=255, null=False)
    notify_at = fields.DatetimeField(null=True)  # NULL → 인앱 전용

    type = fields.CharField(max_length=50, null=False)  # push / email / sms / in_app
    is_read = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notifications"