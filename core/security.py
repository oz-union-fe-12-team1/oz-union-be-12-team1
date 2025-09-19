# core/security.py
import os
from core.config import settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

#fastapi_mail은 python에서 smtp 서버에 연결해서 이메일을 보내주는 패키지
#smtplib -> 파이선 내장되어 편하게 비동기, 메일 템플릿과 fastapi 연동 제공


# 기존: JWT, 비밀번호 해싱 로직들...
# 추가: 이메일 발송

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


# ✅ 수정됨: HTML → text (plain 텍스트 메일 전송)
async def send_verification_email(email: str, code: str):   # ✅ 수정됨
    text_body = f"""
안녕하세요 👋

회원가입을 완료하려면 아래 인증번호를 입력해주세요:

인증 코드: {code}

10분 안에 인증하지 않으면 만료됩니다.
"""   # ✅ 수정됨: text 내용으로 변경

    message = MessageSchema(
        subject="이메일 인증 요청",
        recipients=[email],
        body=text_body,            # ✅ 수정됨: body에 텍스트 직접 전달
        subtype=MessageType.plain  # ✅ 수정됨: plain text 형식
    )
    fm = FastMail(conf)
    await fm.send_message(message)
