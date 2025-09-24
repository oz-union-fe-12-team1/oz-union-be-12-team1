from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any
from models.user import User
from core.security import get_current_user, get_current_admin
from services.inquiries_service import InquiryService
from schemas.inquiries import (
    InquiryCreate,
    InquiryUpdate,
    InquiryOut,
    InquiryListOut,
    InquiryDeleteResponse,
)

router = APIRouter(prefix="/inquiries", tags=["inquiries"])


# -----------------------------
# 1. 문의 작성 (사용자)
# -----------------------------
@router.post("", response_model=InquiryOut)
async def create_inquiry(
    request: InquiryCreate,
    current_user: User = Depends(get_current_user),
) -> InquiryOut:
    inquiry = await InquiryService.create_inquiry(
        user_id=current_user.id,
        title=request.title,
        message=request.message,
    )
    return InquiryOut.from_orm(inquiry)


# -----------------------------
# 2. 내 문의 목록 조회 (사용자)
# -----------------------------
@router.get("/me", response_model=InquiryListOut)
async def get_my_inquiries(current_user: User = Depends(get_current_user)) -> InquiryListOut:
    inquiries = await InquiryService.get_inquiries_by_user(current_user.id)
    return InquiryListOut(
        inquiries=[InquiryOut.from_orm(i) for i in inquiries],
        total=len(inquiries),
    )

# -----------------------------
# 3. 특정 문의 단일 조회 (관리자/본인)
# -----------------------------
@router.get("/{inquiry_id}", response_model=InquiryOut)
async def get_inquiry(
    inquiry_id: int,
    current_user: User = Depends(get_current_user),
) -> InquiryOut:
    inquiry = await InquiryService.get_inquiry_by_id(inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="INQUIRY_NOT_FOUND")

    # 본인 것만 접근 가능 (단, 관리자는 예외)
    if not current_user.is_superuser and inquiry.user != current_user:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    return InquiryOut.from_orm(inquiry)


# -----------------------------
# 4. 전체 문의 목록 조회 (관리자 전용)
# -----------------------------
@router.get("", response_model=InquiryListOut, dependencies=[Depends(get_current_admin)])
async def get_all_inquiries() -> dict[str, Any]:
    inquiries = await InquiryService.get_all_inquiries()
    return {
        "inquiries": [InquiryOut.from_orm(i) for i in inquiries],
        "total": len(inquiries),
    }


# -----------------------------
# 5. 문의 상태/답변 수정 (관리자 전용)
# -----------------------------
@router.patch("/{inquiry_id}", response_model=InquiryOut, dependencies=[Depends(get_current_admin)])
async def update_inquiry(inquiry_id: int, request: InquiryUpdate) -> InquiryOut:
    inquiry = await InquiryService.update_inquiry(
        inquiry_id=inquiry_id,
        status=request.status,
        admin_reply=request.admin_reply,
        replied_at=request.replied_at,
    )
    if not inquiry:
        raise HTTPException(status_code=404, detail="INQUIRY_NOT_FOUND")
    return InquiryOut.from_orm(inquiry)


# -----------------------------
# 6. 문의 삭제 (관리자 or 본인)
# -----------------------------
@router.delete("/{inquiry_id}", response_model=InquiryDeleteResponse)
async def delete_inquiry(
    inquiry_id: int,
    current_user: User = Depends(get_current_user),
) -> InquiryDeleteResponse:
    inquiry = await InquiryService.get_inquiry_by_id(inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="INQUIRY_NOT_FOUND")

    # 본인 것만 삭제 가능 (단, 관리자는 예외)
    if not current_user.is_superuser and inquiry != current_user:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    deleted = await InquiryService.delete_inquiry(inquiry_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="DELETE_FAILED")

    return InquiryDeleteResponse()
