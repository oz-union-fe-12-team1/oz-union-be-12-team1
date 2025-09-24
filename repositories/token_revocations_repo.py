from typing import Optional, List
from models.token_revocations import TokenRevocation
from datetime import datetime


class TokenRevocationsRepository:
    """
    Repository for managing revoked (invalidated) JWT tokens.
    """

    # --------------------
    # CREATE (토큰 무효화 등록)
    # --------------------
    @staticmethod
    async def revoke_token(jti: str, user_id: int) -> TokenRevocation:
        """
        jti: JWT ID (토큰 고유 식별자)
        user_id: 해당 토큰 소유자
        """
        revoked: TokenRevocation = await TokenRevocation.create(
            jti=jti,
            user_id=user_id,
            revoked_at=datetime.utcnow()
        )
        return revoked

    # --------------------
    # READ (특정 토큰 무효화 여부 확인)
    # --------------------
    @staticmethod
    async def is_token_revoked(jti: str) -> bool:
        """
        토큰이 이미 무효화된 경우 True 반환
        """
        exists: bool = await TokenRevocation.filter(jti=jti).exists()
        return exists

    # --------------------
    # READ (사용자별 무효화 토큰 조회)
    # --------------------
    @staticmethod
    async def get_revoked_tokens_by_user(user_id: int) -> List[TokenRevocation]:
        tokens: List[TokenRevocation] = await TokenRevocation.filter(user_id=user_id).all()
        return tokens

    # --------------------
    # DELETE (무효화 토큰 기록 삭제)
    # --------------------
    @staticmethod
    async def delete_revoked_token(jti: str) -> bool:
        deleted_count: int = await TokenRevocation.filter(jti=jti).delete()
        return deleted_count > 0
