from typing import List, Optional
from repositories.inquiries_repo import InquiryRepository
from models.inquiries import Inquiry, InquiryStatus
from datetime import datetime


class InquiryService:
    """
    Service layer for managing Inquiries (문의사항).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_inquiry(user_id: int, title: str, message: str) -> Inquiry:
        """새 문의 작성"""
        return await InquiryRepository.create_inquiry(
            user_id=user_id,
            title=title,
            message=message,
        )

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_inquiry_by_id(inquiry_id: int) -> Optional[Inquiry]:
        """단일 문의 조회"""
        return await InquiryRepository.get_inquiry_by_id(inquiry_id)

    @staticmethod
    async def get_inquiries_by_user(user_id: int) -> List[Inquiry]:
        """사용자별 문의 목록"""
        return await InquiryRepository.get_inquiries_by_user(user_id)

    @staticmethod
    async def get_all_inquiries() -> List[Inquiry]:
        """관리자 전용 전체 문의 목록"""
        return await InquiryRepository.get_all_inquiries()

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
        """관리자 답변 / 상태 / 답변시간 수정"""
        return await InquiryRepository.update_inquiry(
            inquiry_id=inquiry_id,
            status=status,
            admin_reply=admin_reply,
            replied_at=replied_at,
        )

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_inquiry(inquiry_id: int) -> bool:
        """문의 삭제 (사용자 or 관리자)"""
        return await InquiryRepository.delete_inquiry(inquiry_id)
