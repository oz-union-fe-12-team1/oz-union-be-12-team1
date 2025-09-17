from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from .schedule_notifications import ScheduleNotification


class Schedule(Model):
    id = fields.BigIntField(pk=True)  # BIGSERIAL PRIMARY KEY

    user = fields.ForeignKeyField(
        "models.User",
        related_name="schedules",
        on_delete=fields.CASCADE
    )  # user_id: BIGINT NOT NULL, FK(users.id)

    title = fields.CharField(max_length=255, null=False)  # VARCHAR(255) NOT NULL
    description = fields.TextField(null=True)  # TEXT

    start_time = fields.DatetimeField(null=False)  # TIMESTAMPTZ NOT NULL
    end_time = fields.DatetimeField(null=False)  # TIMESTAMPTZ NOT NULL

    all_day = fields.BooleanField(default=False)  # BOOLEAN NOT NULL, DEFAULT FALSE
    location = fields.CharField(max_length=255, null=True)  # VARCHAR(255)

    is_recurring = fields.BooleanField(default=False)  # BOOLEAN NOT NULL, DEFAULT FALSE
    recurrence_rule = fields.TextField(null=True)  # TEXT - 반복 규칙 (RRULE)

    parent_schedule = fields.ForeignKeyField(
        "models.Schedule",
        related_name="children",
        null=True,
        on_delete=fields.SET_NULL
    )  # parent_schedule_id: BIGINT FK(schedules.id)

    reminder_minutes = fields.IntField(null=True)  # INTEGER - 알림 시간(분)

    created_at = fields.DatetimeField(auto_now_add=True)  # TIMESTAMPTZ NOT NULL, DEFAULT now()
    updated_at = fields.DatetimeField(auto_now=True)  # TIMESTAMPTZ NOT NULL, DEFAULT now()
    deleted_at = fields.DatetimeField(null=True)  # TIMESTAMPTZ - 소프트 삭제

    # 역참조 관계
    notifications: fields.ReverseRelation["ScheduleNotification"]

    class Meta:
        table = "schedules"