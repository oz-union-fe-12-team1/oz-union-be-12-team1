from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Boolean, DateTime, 
    Text, Integer, Numeric, CheckConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import CITEXT

Base = declarative_base()


class User(Base):
    """사용자 테이블 모델"""
    __tablename__ = "users"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    
    # 기본 정보
    email = Column(CITEXT, unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    username = Column(CITEXT, nullable=False, index=True)  # NOT NULL로 변경
    profile_image = Column(Text, nullable=True)
    
    # 상태 관리
    is_active = Column(Boolean, nullable=False, default=True)
    is_email_verified = Column(Boolean, nullable=False, default=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, nullable=False, default=0)
    
    # 소셜 로그인
    social_provider = Column(String(32), nullable=True)
    social_id = Column(String(128), nullable=True)
    
    # 타임스탬프
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now(),
        onupdate=func.now()
    )

    # 관계 설정
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    permissions = relationship("UserPermissions", back_populates="user", uselist=False)
    sessions = relationship("UserSession", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")
    todos = relationship("Todo", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    push_subscriptions = relationship("PushSubscription", back_populates="user")

    # 인덱스
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_username_active', 'username', 'is_active'),
        Index('idx_users_social', 'social_provider', 'social_id'),
        Index('idx_users_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"

    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'profile_image': self.profile_image,
            'is_active': self.is_active,
            'is_email_verified': self.is_email_verified,
            'email_verified_at': self.email_verified_at,
            'last_login_at': self.last_login_at,
            'login_count': self.login_count,
            'social_provider': self.social_provider,
            'social_id': self.social_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class UserSettings(Base):
    """사용자 설정 테이블 모델"""
    __tablename__ = "user_settings"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(
        BigInteger, 
        nullable=False, 
        unique=True,
        index=True
    )
    
    # 설정 정보
    timezone = Column(String(64), default='Asia/Seoul')
    language = Column(String(16), default='ko-KR')
    date_format = Column(String(16), default='YYYY-MM-DD')
    time_format = Column(String(16), default='HH:mm')
    theme = Column(String(16), default='system')
    
    # 위치 정보
    default_location_lat = Column(
        Numeric(9, 6), 
        nullable=True,
        # 위도는 -90 ~ 90 범위
    )
    default_location_lon = Column(
        Numeric(9, 6), 
        nullable=True,
        # 경도는 -180 ~ 180 범위
    )
    location_name = Column(String(255), nullable=True)
    
    # 타임스탬프
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now(),
        onupdate=func.now()
    )

    # 관계 설정
    user = relationship("User", back_populates="settings")

    # 제약 조건
    __table_args__ = (
        CheckConstraint(
            'default_location_lat >= -90 AND default_location_lat <= 90',
            name='chk_latitude_range'
        ),
        CheckConstraint(
            'default_location_lon >= -180 AND default_location_lon <= 180',
            name='chk_longitude_range'
        ),
        Index('idx_user_settings_user_id', 'user_id'),
    )

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, timezone='{self.timezone}')>"


class UserPermissions(Base):
    """사용자 권한 테이블 모델"""
    __tablename__ = "user_permissions"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(
        BigInteger, 
        nullable=False, 
        unique=True,
        index=True
    )
    
    # 권한 설정
    notification_permission = Column(Boolean, default=False)
    calendar_permission = Column(Boolean, default=False)
    microphone_permission = Column(Boolean, default=False)
    location_permission = Column(Boolean, default=False)
    
    # 권한 관련 타임스탬프
    permission_requested_at = Column(DateTime(timezone=True), nullable=True)
    last_updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # 타임스탬프
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )

    # 관계 설정
    user = relationship("User", back_populates="permissions")

    # 인덱스
    __table_args__ = (
        Index('idx_user_permissions_user_id', 'user_id'),
        Index('idx_user_permissions_updated', 'last_updated_at'),
    )

    def __repr__(self):
        return f"<UserPermissions(user_id={self.user_id})>"


# 인증 관련 모델들
class EmailVerification(Base):
    """이메일 인증 테이블 모델"""
    __tablename__ = "email_verifications"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(BigInteger, nullable=False, index=True)
    
    # 인증 정보
    token = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(CITEXT, nullable=False)
    is_used = Column(Boolean, nullable=False, default=False)
    
    # 타임스탬프
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    used_at = Column(DateTime(timezone=True), nullable=True)

    # 인덱스
    __table_args__ = (
        Index('idx_email_verifications_token', 'token'),
        Index('idx_email_verifications_user_id', 'user_id'),
        Index('idx_email_verifications_expires', 'expires_at'),
    )

    def __repr__(self):
        return f"<EmailVerification(user_id={self.user_id}, email='{self.email}')>"


class PasswordReset(Base):
    """비밀번호 재설정 테이블 모델"""
    __tablename__ = "password_resets"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(BigInteger, nullable=False, index=True)
    
    # 재설정 정보
    token = Column(String(64), unique=True, nullable=False, index=True)
    is_used = Column(Boolean, nullable=False, default=False)
    
    # 요청 정보
    ip_address = Column(String(45), nullable=True)  # IPv6 지원
    user_agent = Column(Text, nullable=True)
    
    # 타임스탬프
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    used_at = Column(DateTime(timezone=True), nullable=True)

    # 인덱스
    __table_args__ = (
        Index('idx_password_resets_token', 'token'),
        Index('idx_password_resets_user_id', 'user_id'),
        Index('idx_password_resets_expires', 'expires_at'),
    )

    def __repr__(self):
        return f"<PasswordReset(user_id={self.user_id}, token='{self.token[:8]}...')>"