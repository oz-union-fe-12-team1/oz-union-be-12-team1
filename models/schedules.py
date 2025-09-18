from tortoise import fields
from tortoise.models import Model


class Schedule(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="schedules", on_delete=fields.CASCADE)
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    all_day = fields.BooleanField(default=False)
    location = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "schedules"

    def __str__(self):
        return f"Schedule(id={self.id}, user_id={self.user_id}, title={self.title})"
