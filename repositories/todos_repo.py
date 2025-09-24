from typing import List, Optional
from datetime import datetime, timezone
from models.todo import Todo


class TodosRepository:
    """
    Repository for managing Todos (CRUD + soft delete).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_todo(
        user_id: int,
        title: str,
        description: Optional[str] = None,
        schedule_id: Optional[int] = None,
    ) -> Todo:
        """
        새로운 Todo 생성
        - schedule_id가 있으면 해당 일정에 연결
        - schedule_id가 None이면 독립 Todo로 생성
        """
        return await Todo.create(
            user_id=user_id,
            title=title,
            description=description,
            schedule_id=schedule_id,  # ✅ 연결할 일정이 없으면 None 저장
        )

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_todo_by_id(todo_id: int) -> Optional[Todo]:
        """
        ID 기준 단일 Todo 조회
        - Soft Delete 된 데이터는 제외
        """
        return await Todo.get_or_none(id=todo_id, deleted_at=None)

    @staticmethod
    async def get_todos_by_user(user_id: int) -> List[Todo]:
        """
        특정 사용자의 Todo 목록 조회
        - Soft Delete 된 데이터는 제외
        """
        return await Todo.filter(user_id=user_id, deleted_at=None)

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_todo(todo_id: int, **kwargs) -> Optional[Todo]:
        """
        Todo 업데이트
        - kwargs: title, description, is_completed, schedule_id 등
        - schedule_id도 수정 가능 (None이면 일정과 연결 해제)
        """
        todo = await Todo.get_or_none(id=todo_id, deleted_at=None)
        if not todo:
            return None

        for field, value in kwargs.items():
            if hasattr(todo, field) and value is not None:  # ✅ 안전하게 필드 확인 후 반영
                setattr(todo, field, value)

        await todo.save()
        return todo

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_todo(todo_id: int) -> bool:
        """
        Soft Delete (deleted_at만 기록)
        - 실제 데이터는 남아있고 복구 가능
        """
        todo = await Todo.get_or_none(id=todo_id, deleted_at=None)
        if not todo:
            return False

        todo.deleted_at = datetime.now(timezone.utc)  # ✅ UTC 기준 시간 기록
        await todo.save()
        return True

    @staticmethod
    async def hard_delete_todo(todo_id: int) -> int:
        """
        실제 DB에서 완전히 삭제
        - 되돌릴 수 없음
        - 주로 테스트/관리자 기능용
        """
        return await Todo.filter(id=todo_id).delete()
