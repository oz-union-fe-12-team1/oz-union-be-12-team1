from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from .schedules import Schedule
    from .todos import Todo
    from .token_revocations import TokenRevocation
    from .user_locations import UserLocation
    from .inquiries import Inquiry
    from .notifications import Notification


class User(Model):
    id = fields.BigIntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, null=False)
    password_hash = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=50, unique=True, null=False)
    birthday = fields.DateField(null=True)
    profile_image = fields.CharField(max_length=500, null=True)

    # 상태
    is_active = fields.BooleanField(default=True)
    is_email_verified = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)

    # 구글 로그인
    google_id = fields.CharField(max_length=255, unique=True, null=True)
    is_google_user = fields.BooleanField(default=False)

    # 시간
    last_login_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Reverse Relations
    token_revocations: fields.ReverseRelation["TokenRevocation"]
    schedules: fields.ReverseRelation["Schedule"]
    todos: fields.ReverseRelation["Todo"]
    user_locations: fields.ReverseRelation["UserLocation"]
    inquiries: fields.ReverseRelation["Inquiry"]
    notifications: fields.ReverseRelation["Notification"]

    class Meta:
        table = "users"
