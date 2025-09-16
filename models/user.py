from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Boolean, DateTime, 
    Text, Integer, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import CITEXT
from models.base import Base  # 공통 Base 사용


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

    # 관계 설정 - 현재 존재하는 모델들만
    # settings = relationship("UserSettings", back_populates="user", uselist=False)
    # sessions = relationship("UserSession", back_populates="user")
    
    # 미완모델 모델들은 주석 처리
    # permissions = relationship("UserPermissions", back_populates="user", uselist=False)
    # schedules = relationship("Schedule", back_populates="user")
    # todos = relationship("Todo", back_populates="user")
    # chat_sessions = relationship("ChatSession", back_populates="user")
    # push_subscriptions = relationship("PushSubscription", back_populates="user")

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