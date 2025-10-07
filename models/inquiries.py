from tortoise import fields, ForeignKeyFieldInstance
from tortoise.models import Model
import enum

from models.user import User


class InquiryStatus(str, enum.Enum):  # ✅ 오타 수정 (Inquiriy → Inquiry)
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class Inquiry(Model):
    id = fields.BigIntField(pk=True)
    user: ForeignKeyFieldInstance[User] = fields.ForeignKeyField(
        "models.User",
        related_name="inquiries",
        on_delete=fields.CASCADE,
        null=False
    )

    user_id: int
    # FK → 문의 작성 사용자

    title = fields.CharField(max_length=255, null=False)
    # 문의 제목

    message = fields.TextField(null=False)
    # 문의 내용

    status = fields.CharEnumField(
        enum_type=InquiryStatus,   # ✅ 올바른 enum 참조
        default=InquiryStatus.pending
    )
    # 처리 상태

    admin_reply = fields.TextField(null=True)
    # 관리자 답변 내용 (NULL 가능)

    replied_at = fields.DatetimeField(null=True)
    # 답변 완료 시각

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "inquiries"
