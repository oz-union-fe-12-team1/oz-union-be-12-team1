from typing import Optional
from models.token_revocations import TokenRevocation
from tortoise.exceptions import DoesNotExist
from datetime import datetime


class TokenRevocationsRepository:
    """
    Repository for managing revoked (invalidated) JWT tokens.
    """

    # ✅ Create (토큰 무효화 등록)
    @staticmethod
    async def revoke_token(jti: str, user_id: int) -> TokenRevocation:
        """
        jti: JWT ID (토큰 고유 식별자)
        user_id: 해당 토큰 소유자
        """
        revoked = await TokenRevocation.create(
            jti=jti,
            user_id=user_id,
            revoked_at=datetime.utcnow()
        )
        return revoked

    # ✅ Read (특정 토큰 무효화 여부 확인)
    @staticmethod
    async def is_token_revoked(jti: str) -> bool:
        """
        토큰이 이미 무효화된 경우 True 반환
        """
        return await TokenRevocation.filter(jti=jti).exists()

    # ✅ Read (사용자별 무효화 토큰 조회)
    @staticmethod
    async def get_revoked_tokens_by_user(user_id: int):
        return await TokenRevocation.filter(user_id=user_id).all()

    # ✅ Delete (무효화 토큰 기록 삭제 – 보통 유지하지만, 관리 차원에서 필요 시)
    @staticmethod
    async def delete_revoked_token(jti: str) -> bool:
        deleted_count = await TokenRevocation.filter(jti=jti).delete()
        return deleted_count > 0
