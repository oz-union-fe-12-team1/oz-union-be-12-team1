from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.BigIntField(pk=True)

    email = fields.CharField(max_length=255, unique=True, null=False)
    password_hash = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=50, null=False)

    birthday = fields.DateField(null=True)
    profile_image = fields.CharField(max_length=500, null=True)

    is_active = fields.BooleanField(default=True)
    is_email_verified = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)

    google_id = fields.CharField(max_length=255, unique=True, null=True)

    last_login_at = fields.DatetimeField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"
