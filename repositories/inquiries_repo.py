from typing import List, Optional
from tortoise.exceptions import DoesNotExist
from models.inquiries import Inquiry, InquiryStatus


class InquiriesRepository:
    """
    Repository for managing Inquiry (문의사항) data.
    """

    # ✅ Create (문의 작성)
    @staticmethod
    async def create_inquiry(user_id: int, title: str, message: str) -> Inquiry:
        inquiry = await Inquiry.create(
            user_id=user_id,
            title=title,
            message=message,
            status=InquiryStatus.pending,  # 기본 상태 = 대기중
        )
        return inquiry

    # ✅ Read (단일 조회)
    @staticmethod
    async def get_inquiry_by_id(inquiry_id: int) -> Optional[Inquiry]:
        try:
            return await Inquiry.get(id=inquiry_id)
        except DoesNotExist:
            return None

    # ✅ Read (사용자별 문의 목록)
    @staticmethod
    async def get_inquiries_by_user(user_id: int) -> List[Inquiry]:
        return await Inquiry.filter(user_id=user_id).order_by("-created_at")

    # ✅ Update (관리자 답변 달기 + 상태 변경)
    @staticmethod
    async def reply_to_inquiry(inquiry_id: int, reply: str, status: InquiryStatus) -> Optional[Inquiry]:
        try:
            inquiry = await Inquiry.get(id=inquiry_id)
            inquiry.admin_reply = reply
            inquiry.status = status
            await inquiry.save()
            return inquiry
        except DoesNotExist:
            return None

    # ✅ Delete (사용자 요청으로 문의 삭제)
    @staticmethod
    async def delete_inquiry(inquiry_id: int) -> bool:
        deleted_count = await Inquiry.filter(id=inquiry_id).delete()
        return deleted_count > 0
