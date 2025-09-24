from tortoise import fields, ForeignKeyFieldInstance
from tortoise.models import Model

from models.user import User


class UserLocation(Model):
    id = fields.BigIntField(pk=True)

    user: ForeignKeyFieldInstance[User] = fields.ForeignKeyField(
        "models.User",
        related_name="locations",
        on_delete=fields.CASCADE,
        null=False
    )
    # FK → 사용자

    latitude = fields.DecimalField(max_digits=9, decimal_places=6, null=False)
    longitude = fields.DecimalField(max_digits=9, decimal_places=6, null=False)
    # 위도 / 경도

    label = fields.CharField(max_length=100, null=True)
    # 위치 라벨 (예: 집, 회사 등)

    is_default = fields.BooleanField(default=False)
    # 기본 위치 여부

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_locations"
        indexes = (("user_id", "is_default"),)
