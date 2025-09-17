from tortoise import fields
from tortoise.models import Model


class UserLocations(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="locations",
        on_delete=fields.CASCADE
    )
    latitude = fields.DecimalField(max_digits=9, decimal_places=6)
    longitude = fields.DecimalField(max_digits=9, decimal_places=6)
    location_name = fields.CharField(max_length=100, null=True)
    is_default = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_locations"

    def str(self):
        return f"UserLocation(id={self.id}, user={self.user_id}, name={self.location_name}, default={self.is_default})"
