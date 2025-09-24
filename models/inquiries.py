from __future__ import annotations  # 🔑 forward reference
from typing import TYPE_CHECKING, Optional
from datetime import datetime
from tortoise import fields
from tortoise.models import Model
import enum

if TYPE_CHECKING:
    from models.user import User


class InquiryStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class Inquiry(Model):
    id = fields.BigIntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="inquiries",
        on_delete=fields.CASCADE,
        null=False,
    )
    # FK → 문의 작성 사용자

    title = fields.CharField(max_length=255, null=False)
    message = fields.TextField(null=False)

    status = fields.CharEnumField(
        enum_type=InquiryStatus,
        default=InquiryStatus.pending,
    )
    # 처리 상태

    admin_reply = fields.TextField(null=True)
    replied_at = fields.DatetimeField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "inquiries"
