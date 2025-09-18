from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from .schedules import schedule
    from .todos import todos
    from .token_revocations import token_revocations
    from .user_locations import user_locations
    from .inquiries import inauiries
    from .notifications import notifications

class User(Model):
    id = fields.BigIntField(pk=True)  # BIGSERIAL PRIMARY KEY
    email = fields.CharField(max_length=255, unique=True, null=False)  # CITEXT UNIQUE, NOT NULL
    password_hash = fields.CharField(max_length=255, null=False)  # TEXT NOT NULL
    username = fields.CharField(max_length=100, null=False)  # CITEXT NOT NULL (기존 nullable에서 변경)
    birthday = fields.DateField(null=False)
    profile_image = fields.TextField(null=True)  # TEXT

    # 상태 관련 필드
    is_active = fields.BooleanField(default=True)  # BOOLEAN NOT NULL, DEFAULT TRUE
    is_email_verified = fields.BooleanField(default=False)  # BOOLEAN NOT NULL, DEFAULT FALSE
    is_superuser = fields.BooleanField(default=False)  # BOOLEAN NOT NULL, DEFAULT FALSE

    # 새로 추가된 시간 관련 필드
    email_verified_at = fields.DatetimeField(null=True)  # TIMESTAMPTZ
    last_login_at = fields.DatetimeField(null=True)  # TIMESTAMPTZ
    login_count = fields.IntField(default=0)  # INTEGER NOT NULL, DEFAULT 0
    
    #구글 소셜 로그인
    google_id = fields.CharField(max_length=255, unique=True, null=True)  # VARCHAR(255) UNIQUE, NULL 허용 - 구글 계정 고유 ID (sub)
    is_google_user = fields.BooleanField(default=False)  # BOOLEAN DEFAULT false - 구글 소셜 로그인 여부
    
    # 기본 시간 필드
    last_login_at = fields.DatetimeField(null=True)  # TIMESTAMPTZ NULL 가능 - 최근 로그인 시간
    created_at = fields.DatetimeField(auto_now_add=True)  # TIMESTAMPTZ NOT NULL, DEFAULT now()
    updated_at = fields.DatetimeField(auto_now=True)  # TIMESTAMPTZ NOT NULL, DEFAULT now()

    # 관계 (reverse relation) - 스프레드시트 기반으로 업데이트
    token_revocations: fields.ReverseRelation["token_revocations"]
    schedules: fields.ReverseRelation["Schedule"]
    todos: fields.ReverseRelation["Todo"]
    user_locations: fields.ReverseRelation["user_locations"]
    inquiries: fields.ReverseRelation["inauiries"]
    notifications: fields.ReverseRelation["notifications"]

    class Meta:
        table = "users"  # 테이블명 유지