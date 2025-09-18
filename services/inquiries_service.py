from typing import List, Optional
from repositories.inquiries_repo import InquiryRepository  # ✅ 단수형으로 맞춤
from models.inquiries import Inquiry, InquiryStatus


class InquiryService:
    """
    Service layer for managing Inquiries (문의사항).
    """

    # ✅ Create (문의 작성)
    @staticmethod
    async def create_inquiry(user_id: int, title: str, message: str) -> Inquiry:
        return await InquiryRepository.create_inquiry(
            user_id=user_id,
            title=title,
            message=message
        )

    # ✅ Read (단일 조회)
    @staticmethod
    async def get_inquiry_by_id(inquiry_id: int) -> Optional[Inquiry]:
        return await InquiryRepository.get_inquiry_by_id(inquiry_id)

    # ✅ Read (사용자별 문의 목록)
    @staticmethod
    async def get_inquiries_by_user(user_id: int) -> List[Inquiry]:
        return await InquiryRepository.get_inquiries_by_user(user_id)

    # ✅ Update (관리자 답변 등록 + 상태 변경)
    @staticmethod
    async def reply_to_inquiry(inquiry_id: int, reply: str, status: InquiryStatus) -> Optional[Inquiry]:
        return await InquiryRepository.reply_to_inquiry(
            inquiry_id=inquiry_id,
            reply=reply,
            status=status
        )

    # ✅ Update (문의 상태만 변경)
    @staticmethod
    async def update_status(inquiry_id: int, status: InquiryStatus) -> Optional[Inquiry]:
        return await InquiryRepository.update_status(
            inquiry_id=inquiry_id,
            status=status
        )

    # ✅ Delete (사용자 요청 → 문의 삭제)
    @staticmethod
    async def delete_inquiry(inquiry_id: int) -> bool:
        return await InquiryRepository.delete_inquiry(inquiry_id)
