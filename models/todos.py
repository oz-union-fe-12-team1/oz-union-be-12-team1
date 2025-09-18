from tortoise import fields
from tortoise.models import Model


class Todo(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="todos", on_delete=fields.CASCADE)
    schedule = fields.ForeignKeyField("models.Schedule", related_name="todos", null=True, on_delete=fields.SET_NULL)
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    is_completed = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "todos"

    def __str__(self):
        return f"Todo(id={self.id}, user_id={self.user_id}, title={self.title}, completed={self.is_completed})"

