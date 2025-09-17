from tortoise import fields
from tortoise.models import Model


class UserSettings(Model):
    id = fields.IntField(pk=True)
    user = fields.OneToOneField(
        "models.User",
        related_name="settings",
        on_delete=fields.CASCADE
    )

    language = fields.CharField(max_length=50, null=True)
    date_format = fields.CharField(max_length=20, null=True)
    time_format = fields.CharField(max_length=20, null=True)

    default_location_lat = fields.DecimalField(max_digits=9, decimal_places=6, null=True)
    default_location_lon = fields.DecimalField(max_digits=9, decimal_places=6, null=True)
    location_name = fields.CharField(max_length=100, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_settings"