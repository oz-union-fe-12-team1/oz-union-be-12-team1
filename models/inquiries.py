from typing import TYPE_CHECKING, Optional
from tortoise import fields
from tortoise.models import Model
import enum
from datetime import datetime

if TYPE_CHECKING:
    from models.user import User


class InquiryStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class Inquiry(Model):
    id: int = fields.BigIntField(pk=True)

    user: "User" = fields.ForeignKeyField(
        "models.User",
        related_name="inquiries",
        on_delete=fields.CASCADE,
        null=False
    )
    # FK → 문의 작성 사용자

    title: str = fields.CharField(max_length=255, null=False)
    message: str = fields.TextField(null=False)

    status: InquiryStatus = fields.CharEnumField(
        enum_type=InquiryStatus,
        default=InquiryStatus.pending,
    )

    admin_reply: Optional[str] = fields.TextField(null=True)
    replied_at: Optional[datetime] = fields.DatetimeField(null=True)

    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "inquiries"
