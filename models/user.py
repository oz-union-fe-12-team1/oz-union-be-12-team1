from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from .user_settings import UserSettings
    from .user_sessions import UserSession
    from .schedules import Schedule
    from .todo import Todo
    from .notifications import Notification
    from .api_usage_logs import APIUsageLog
    from .ai_conversations import AIConversation


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, null=False)
    password_hash = fields.CharField(max_length=255, null=False)

    pw_reset_token = fields.CharField(max_length=255, null=True)
    pw_reset_requested_at = fields.DatetimeField(null=True)

    username = fields.CharField(max_length=100, unique=True, null=True)
    birthday = fields.DateField(null=False)
    profile_image = fields.CharField(max_length=255, null=True)

    is_active = fields.BooleanField(default=True)
    is_email_verified = fields.BooleanField(default=False)
    last_login_at = fields.DatetimeField(null=True)

    social_provider = fields.CharField(max_length=50, null=True)
    social_id = fields.CharField(max_length=255, null=True)

    is_superuser = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 관계 (reverse relation)
    settings: fields.ReverseRelation["UserSettings"]
    sessions: fields.ReverseRelation["UserSession"]
    schedules: fields.ReverseRelation["Schedule"]
    todos: fields.ReverseRelation["Todo"]
    notifications: fields.ReverseRelation["Notification"]
    api_usage_logs: fields.ReverseRelation["APIUsageLog"]
    ai_conversations: fields.ReverseRelation["AIConversation"]

    class Meta:
        table = "users"