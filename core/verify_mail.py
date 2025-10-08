from fastapi.security import HTTPBearer
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import SecretStr
from .config import settings

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

