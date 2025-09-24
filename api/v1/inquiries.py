from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from core.security import get_current_user, get_current_admin
from services.inquiries_service import InquiryService
from schemas.inquiries import (
    InquiryCreateRequest,
    InquiryUpdateRequest,
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
    request: InquiryCreateRequest,
    current_user: User = Depends(get_current_user),
):
    return await InquiryService.create_inquiry(
        user_id=current_user.id,
        request=request,
    )


# -----------------------------
# 2. 내 문의 목록 조회 (사용자)
# -----------------------------
@router.get("/me", response_model=InquiryListOut)
async def get_my_inquiries(current_user: User = Depends(get_current_user)):
    return await InquiryService.get_inquiries_by_user(current_user.id)


# -----------------------------
# 3. 특정 문의 단일 조회 (관리자/본인)
# -----------------------------
@router.get("/{inquiry_id}", response_model=InquiryOut)
async def get_inquiry(
    inquiry_id: int,
    current_user: User = Depends(get_current_user),
):
    inquiry = await InquiryService.get_inquiry_by_id(inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="INQUIRY_NOT_FOUND")

    # 본인 것만 접근 가능 (단, 관리자는 예외)
    if not current_user.is_superuser and inquiry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    return inquiry


# -----------------------------
# 4. 전체 문의 목록 조회 (관리자 전용)
# -----------------------------
@router.get("", response_model=InquiryListOut, dependencies=[Depends(get_current_admin)])
async def get_all_inquiries():
    return await InquiryService.get_all_inquiries()


# -----------------------------
# 5. 문의 상태/답변 수정 (관리자 전용)
# -----------------------------
@router.patch("/{inquiry_id}", response_model=InquiryOut, dependencies=[Depends(get_current_admin)])
async def update_inquiry(inquiry_id: int, request: InquiryUpdateRequest):
    inquiry = await InquiryService.update_inquiry(inquiry_id, request)
    if not inquiry:
        raise HTTPException(status_code=404, detail="INQUIRY_NOT_FOUND")
    return inquiry


# -----------------------------
# 6. 문의 삭제 (관리자 or 본인)
# -----------------------------
@router.delete("/{inquiry_id}", response_model=InquiryDeleteResponse)
async def delete_inquiry(
    inquiry_id: int,
    current_user: User = Depends(get_current_user),
):
    inquiry = await InquiryService.get_inquiry_by_id(inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="INQUIRY_NOT_FOUND")

    # 본인 것만 삭제 가능 (단, 관리자는 예외)
    if not current_user.is_superuser and inquiry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    deleted = await InquiryService.delete_inquiry(inquiry_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="DELETE_FAILED")

    return {"message": "Inquiry deleted successfully"}

# 이미 서비스에서 변환하고 있음 그래서 충돌이 발생함 / 수정 완료