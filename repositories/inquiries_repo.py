from typing import List, Optional
from datetime import datetime
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

    @staticmethod
    async def get_all_inquiries() -> List[Inquiry]:
        """관리자 전용 전체 문의 목록 조회"""
        return await Inquiry.all().order_by("-created_at")

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_inquiry(
        inquiry_id: int,
        status: Optional[InquiryStatus] = None,
        admin_reply: Optional[str] = None,
        replied_at: Optional[datetime] = None,
    ) -> Optional[Inquiry]:
        """관리자 답변/상태/답변시간 수정"""
        try:
            inquiry = await Inquiry.get(id=inquiry_id)
            if status is not None:
                inquiry.status = status
            if admin_reply is not None:
                inquiry.admin_reply = admin_reply
            if replied_at is not None:
                inquiry.replied_at = replied_at
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
        deleted_count: int = await Inquiry.filter(id=inquiry_id).delete()
        return deleted_count > 0
