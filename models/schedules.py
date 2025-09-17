from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model
import enum

class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

if TYPE_CHECKING:
    from .todo import Todo
    from .notifications import Notification


class Schedule(Model):
    id = fields.IntField(pk=True)

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

    priority = fields.CharEnumField(
        enum_type=Priority,
        null=True
    )

    is_recurring = fields.BooleanField(default=False)
    recurrence_rule = fields.CharField(max_length=255, null=True)

    parent_schedule = fields.ForeignKeyField(
        "models.Schedule",
        related_name="children",
        null=True,
        on_delete=fields.SET_NULL
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 역참조 관계
    todos: fields.ReverseRelation["Todo"]
    notifications: fields.ReverseRelation["Notification"]

    class Meta:
        table = "schedules"