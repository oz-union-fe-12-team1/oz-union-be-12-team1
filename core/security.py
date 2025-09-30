import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import SecretStr

from core.config import settings
from models.user import User

# ========================
# 메일 발송 설정
# ========================
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

bearer_scheme = HTTPBearer(
    description="로그인(/auth/login)에서 발급받은 Bearer Token을 입력하세요."
)

async def send_verification_email(email: str, code: str) -> None:
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
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:

    # 1) 우선 쿠키 확인
    token = request.cookies.get("access_token")
    print(token)
    # 2) 쿠키 없으면 Authorization 헤더 확인 (Swagger/Postman용 fallback)
    if not token and credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NOT_AUTHENTICATED"
        )

    # JWT 디코드
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_EXPIRED")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_INVALID")

    # DB에서 유저 조회
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
