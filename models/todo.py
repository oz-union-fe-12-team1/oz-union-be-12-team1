from tortoise import fields
from tortoise.models import Model
import enum


class TodoPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TodoStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class Todo(Model):
    id = fields.BigIntField(pk=True)  # BIGSERIAL PRIMARY KEY

    user = fields.ForeignKeyField(
        "models.User",
        related_name="todos",
        on_delete=fields.CASCADE
    )  # user_id: BIGINT NOT NULL, FK(users.id)
    
    subject_id = fields.BigIntField(null=True)  # BIGINT FK(subjects.id) - 과목 ID
    
    title = fields.CharField(max_length=255, null=False)  # VARCHAR(255) NOT NULL
    description = fields.TextField(null=True)  # TEXT
    due_date = fields.DateField(null=True)  # DATE
    
    priority = fields.CharEnumField(
        enum_type=TodoPriority,
        default=TodoPriority.medium
    )  # todo_priority DEFAULT 'medium'
    
    status = fields.CharEnumField(
        enum_type=TodoStatus,
        default=TodoStatus.pending
    )  # todo_status DEFAULT 'pending'
    
    created_at = fields.DatetimeField(auto_now_add=True)  # TIMESTAMPTZ NOT NULL, DEFAULT now()
    updated_at = fields.DatetimeField(auto_now=True)  # TIMESTAMPTZ NOT NULL, DEFAULT now()
    completed_at = fields.DatetimeField(null=True)  # TIMESTAMPTZ

    class Meta:
        table = "todos"  # 스프레드시트 테이블명