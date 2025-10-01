import jwt
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import settings
from models.user import User
from datetime import datetime, timedelta

# bearer_scheme = HTTPBearer(
#     description="로그인(/auth/login)에서 발급받은 Bearer Token을 입력하세요."
# )
# credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)

#JWT 생성 관련 (access-token 발급)

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ========================
# 인증/인가 유틸
# ========================
async def get_current_user(request: Request, response: Response) -> User:
    # 1) 쿠키 확인
    token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(status_code=401, detail="NOT_AUTHENTICATED")

    user_id: int | None = None

    # 2) Access Token 검증
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="INVALID_ACCESS_TOKEN")
        user_id = int(sub)

    except jwt.ExpiredSignatureError:
        # 3) Access Token 만료 → Refresh Token 확인
        if not refresh_token:
            raise HTTPException(status_code=401, detail="TOKEN_EXPIRED")

        try:
            refresh_payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            sub = refresh_payload.get("sub")
            if not sub:
                raise HTTPException(status_code=401, detail="INVALID_REFRESH_TOKEN")

            user_id = int(sub)

            # 새로운 Access Token 재발급 + 쿠키 갱신
            new_access = create_access_token(user_id)
            response.set_cookie(
                "access_token",
                value=new_access,
                httponly=True,
                secure=True,
                samesite="none"
            )

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="REFRESH_TOKEN_EXPIRED")
        except Exception:
            raise HTTPException(status_code=401, detail="INVALID_REFRESH_TOKEN")

    except Exception:
        raise HTTPException(status_code=401, detail="TOKEN_INVALID")

    # 4) DB 조회
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=401, detail="USER_NOT_FOUND")

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """관리자 권한 확인"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="NOT_ENOUGH_PRIVILEGES")
    return current_user