from typing import List, Optional
from repositories.inquiries_repo import InquiryRepository
from schemas.inquiries import (
    InquiryCreateRequest,
    InquiryOut,
    InquiryListOut,
    InquiryUpdateRequest,
)
from models.inquiries import Inquiry, InquiryStatus


class InquiryService:
    """
    Service layer for managing Inquiries (문의사항).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_inquiry(user_id: int, request: InquiryCreateRequest) -> InquiryOut:
        """새 문의 작성"""
        inquiry: Inquiry = await InquiryRepository.create_inquiry(
            user_id=user_id,
            title=request.title,
            message=request.message,
        )
        return InquiryOut.model_validate(inquiry, from_attributes=True)

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_inquiry_by_id(inquiry_id: int) -> Optional[InquiryOut]:
        """단일 문의 조회"""
        inquiry = await InquiryRepository.get_inquiry_by_id(inquiry_id)
        if not inquiry:
            return None
        return InquiryOut.model_validate(inquiry, from_attributes=True)

    @staticmethod
    async def get_inquiries_by_user(user_id: int) -> InquiryListOut:
        """특정 사용자의 문의 목록 조회"""
        inquiries: List[Inquiry] = await InquiryRepository.get_inquiries_by_user(user_id)
        return InquiryListOut(
            inquiries=[InquiryOut.model_validate(i, from_attributes=True) for i in inquiries],
            total=len(inquiries),
        )

    @staticmethod
    async def get_all_inquiries() -> InquiryListOut:
        """관리자 전용 전체 문의 목록 조회"""
        inquiries: List[Inquiry] = await InquiryRepository.get_all_inquiries()
        return InquiryListOut(
            inquiries=[InquiryOut.model_validate(i, from_attributes=True) for i in inquiries],
            total=len(inquiries),
        )

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_inquiry(inquiry_id: int, request: InquiryUpdateRequest) -> Optional[InquiryOut]:
        """
        관리자 답변/상태/답변시간 수정
        - status: InquiryStatus
        - admin_reply: str
        - replied_at: datetime
        """
        inquiry = await InquiryRepository.update_inquiry(
            inquiry_id=inquiry_id,
            status=request.status,
            admin_reply=request.admin_reply,
            replied_at=request.replied_at,
        )
        if not inquiry:
            return None
        return InquiryOut.model_validate(inquiry, from_attributes=True)

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_inquiry(inquiry_id: int) -> bool:
        """사용자 요청에 따른 문의 삭제"""
        return await InquiryRepository.delete_inquiry(inquiry_id)
