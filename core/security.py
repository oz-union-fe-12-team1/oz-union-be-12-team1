import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from core.config import settings
from models.user import User

# ========================
# 메일 발송 설정
# ========================
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

async def send_verification_email(email: str, code: str):
    """회원가입 인증 메일 발송 (plain text)"""
    text_body = f"""
안녕하세요 👋

회원가입을 완료하려면 아래 인증번호를 입력해주세요:

인증 코드: {code}

10분 안에 인증하지 않으면 만료됩니다.
"""

    message = MessageSchema(
        subject="이메일 인증 요청",
        recipients=[email],
        body=text_body,
        subtype=MessageType.plain,
    )
    fm = FastMail(conf)
    await fm.send_message(message)


# ========================
# 인증/인가 유틸
# ========================
# Bearer Token 전용
bearer_scheme = HTTPBearer(description="로그인(/auth/login)에서 발급받은 Bearer Token을 입력하세요.")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> User:
    """JWT 토큰에서 현재 로그인한 사용자 조회"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_EXPIRED")
    except Exception:  # InvalidTokenError 포함
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_INVALID")

    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="USER_NOT_FOUND")

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """관리자 권한 확인"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="NOT_ENOUGH_PRIVILEGES"
        )
    return current_user
