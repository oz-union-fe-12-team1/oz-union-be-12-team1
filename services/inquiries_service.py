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

    # user 문의내역 수정
    @staticmethod
    async def update_inquiry_user(
            inquiry_id: int,
            user_id: int,
            title: Optional[str] = None,
            message: Optional[str] = None
    ) -> Optional[Inquiry]:
        inquiry = await InquiryRepository.get_inquiry_by_id(inquiry_id)
        if not inquiry:
            return None

        # 본인만 수정 가능
        if inquiry.user_id != user_id:  # ✅ user_id 바로 비교 가능
            return None

        # 이미 답변된 건 수정 불가
        if inquiry.admin_reply:
            return None

        return await InquiryRepository.update_inquiry_user(inquiry_id, title, message)

    @staticmethod
    async def update_inquiry(
        inquiry_id: int,
        status: Optional[str] = None,
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
