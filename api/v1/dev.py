from fastapi import APIRouter, HTTPException
from models.user import User
from passlib.hash import bcrypt
from schemas.user import AdminUserOut   # ✅ 응답 스키마에 맞춤

router = APIRouter(prefix="/dev", tags=["dev"])  # ⚠️ 운영 전 반드시 제거할 것!

# -----------------------------
# 슈퍼유저 생성 (임시)
# -----------------------------
@router.post("/create-superuser", response_model=AdminUserOut)
async def create_superuser(
    email: str,
    password: str,
    username: str = "admin"
):
    """
    ⚠️ 개발용 엔드포인트
    - 운영 배포 전 반드시 삭제하거나 주석 처리하세요.
    - 최초 관리자 계정을 만들 때만 사용하세요.
    """
    existing = await User.get_or_none(email=email)
    if existing:
        raise HTTPException(status_code=400, detail="USER_ALREADY_EXISTS")

    hashed_password = bcrypt.hash(password)
    user = await User.create(
        email=email,
        password_hash=hashed_password,
        username=username,
        birthday="2000-01-01",  # ✅ 임시 값 (명세서 요구 반영 필요시 수정)
        is_email_verified=True,
        is_superuser=True,
        is_active=True
    )

    return AdminUserOut.from_orm(user)  # ✅ 응답 스키마 변환
