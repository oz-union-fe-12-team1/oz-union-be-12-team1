from typing import Optional, List
from passlib.hash import bcrypt
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from datetime import date
from models.user import User


class UserRepository:
    """
    Repository for managing User data (CRUD + 인증 관련 조회).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_user(
        email: str,
        password_hash: str,
        username: str,
        birthday: date,
    ) -> User:
        """회원가입 (이메일 인증 후 최종 가입)"""
        user = await User.create(
            email=email,
            password_hash=password_hash,
            username=username,
            birthday=birthday,
            is_email_verified=True,  # 인증 완료 상태로 저장
            is_google_user=False, # 구글 로그인 일시 True로 / 기본 False
            is_active=True,
            is_superuser=False,
        )
        return user

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """ID 기준 단일 조회"""
        try:
            return await User.get(id=user_id)
        except DoesNotExist:
            return None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """이메일 기준 단일 조회"""
        return await User.filter(email=email).first()

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """이름 기준 단일 조회"""
        return await User.filter(username=username).first()

    @staticmethod
    async def get_all_users() -> List[User]:
        """관리자 전용 전체 사용자 조회"""
        return await User.all().order_by("-created_at")

    @staticmethod
    async def search_users(keyword: str) -> list[dict]:
        """
        유저 이름 또는 이메일 '부분 검색' (대소문자 무시)
        ex) 'oh' → oh, ohna, ohnana 전부 조회
        """
        users = await User.filter(
            Q(username__icontains=keyword) | Q(email__icontains=keyword)
        ).values(
            "id",
            "email",
            "username",
            "is_active",
            "is_email_verified",
            "is_superuser",
            "google_id",
            "last_login_at",
            "created_at",
            "updated_at",
        )
        #구글 아이디 존재 여부
        for u in users:
            u["is_googleuser"] = bool(u.get("social_id"))

        return users
    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def verify_user(user_id: int) -> Optional[User]:
        """
        (보조용) 이메일 인증 완료 상태로 업데이트.
        현재 플로우에서는 잘 안 쓰이지만,
        관리자가 수동으로 인증 처리할 때 사용 가능.
        """
        user = await User.get_or_none(id=user_id)
        if not user:
            return None
        user.is_email_verified = True
        await user.save()
        return user

    @staticmethod
    async def update_profile(
        user_id: int,
        username: Optional[str] = None,
        bio: Optional[str] = None,
        profile_image: Optional[str] = None,
    ) -> Optional[User]:
        """프로필 수정"""
        user = await User.get_or_none(id=user_id)
        if not user:
            return None

        if username is not None:
            user.username = username
        if bio is not None:
            user.bio = bio
        if profile_image is not None:
            user.profile_image = profile_image

        await user.save()
        return user

    @staticmethod
    async def update_password(user: User, new_password: str) -> User:
        """
        주어진 User 객체의 비밀번호를 새로운 값으로 해시 후 저장한다.
        """
        user.password_hash = bcrypt.hash(new_password)
        await user.save()
        return user

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """회원 탈퇴"""
        user = await User.get_or_none(id=user_id)
        if not user:
            return False
        await user.delete()
        return True

#롼리자 전체 유저 접속시간 통게용
    @staticmethod
    async def get_all_users_last_login() -> list[dict]:
        from models.user import User
        users = await User.all().values("id", "email", "username", "last_login_at")
        # 한국시간으로 포맷팅
        from datetime import timezone, timedelta
        KST = timezone(timedelta(hours=9))
        formatted = []
        for u in users:
            if u["last_login_at"]:
                u["last_login_at"] = u["last_login_at"].astimezone(KST).strftime("%Y-%m-%d %H:%M")
            formatted.append(u)
        return formatted