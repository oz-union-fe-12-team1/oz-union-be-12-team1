from typing import List, Optional
from tortoise.exceptions import DoesNotExist
from models.inquiries import Inquiry, InquiryStatus


class InquiryRepository:
    """
    Repository for managing Inquiry (문의사항) data.
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_inquiry(user_id: int, title: str, message: str) -> Inquiry:
        """새 문의 작성"""
        return await Inquiry.create(
            user_id=user_id,
            title=title,
            message=message,
            status=InquiryStatus.pending,  # 기본 상태 = 대기중
        )

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_inquiry_by_id(inquiry_id: int) -> Optional[Inquiry]:
        """단일 문의 조회"""
        try:
            return await Inquiry.get(id=inquiry_id)
        except DoesNotExist:
            return None

    @staticmethod
    async def get_inquiries_by_user(user_id: int) -> List[Inquiry]:
        """사용자별 문의 목록 조회"""
        return await Inquiry.filter(user_id=user_id).order_by("-created_at")

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def reply_to_inquiry(inquiry_id: int, reply: str, status: InquiryStatus) -> Optional[Inquiry]:
        """관리자 답변 등록 + 상태 변경"""
        try:
            inquiry = await Inquiry.get(id=inquiry_id)
            inquiry.admin_reply = reply
            inquiry.status = status
            await inquiry.save()
            return inquiry
        except DoesNotExist:
            return None

    @staticmethod
    async def update_status(inquiry_id: int, status: InquiryStatus) -> Optional[Inquiry]:
        """문의 상태만 변경"""
        try:
            inquiry = await Inquiry.get(id=inquiry_id)
            inquiry.status = status
            await inquiry.save()
            return inquiry
        except DoesNotExist:
            return None

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_inquiry(inquiry_id: int) -> bool:
        """사용자 요청에 따라 문의 삭제"""
        deleted_count = await Inquiry.filter(id=inquiry_id).delete()
        return deleted_count > 0
