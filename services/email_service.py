from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from core.config import settings
from pydantic import SecretStr


# config에서 mail 사용하는 값 묶기

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM or settings.MAIL_USERNAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
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