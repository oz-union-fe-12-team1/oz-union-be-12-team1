from __future__ import annotations
from datetime import date, datetime
from tortoise import fields
from tortoise.models import Model


class User(Model):
    id: int = fields.BigIntField(pk=True)

    email: str = fields.CharField(max_length=255, unique=True, null=False)
    password_hash: str | None = fields.CharField(max_length=255, null=True)
    username: str = fields.CharField(max_length=50, unique=False, null=False)

    birthday: date | None = fields.DateField(null=True)
    profile_image: str | None = fields.CharField(max_length=500, null=True)

    is_active: bool = fields.BooleanField(default=True)
    is_email_verified: bool = fields.BooleanField(default=False)
    is_superuser: bool = fields.BooleanField(default=False)

    google_id: str | None = fields.CharField(max_length=255, unique=True, null=True)

    last_login_at: datetime | None = fields.DatetimeField(null=True)

    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"
