from typing import List, Optional
from datetime import datetime
from models.todo import Todo


class TodoRepository:
    @staticmethod
    async def create_todo(
        user_id: int,
        title: str,
        description: Optional[str] = None,
        schedule_id: Optional[int] = None,
    ) -> Todo:
        """새로운 Todo 생성"""
        return await Todo.create(
            user_id=user_id,
            title=title,
            description=description,
            schedule_id=schedule_id,
        )

    @staticmethod
    async def get_todo(todo_id: int) -> Optional[Todo]:
        """ID 기준 단일 Todo 조회 (삭제되지 않은 것만)"""
        return await Todo.get_or_none(id=todo_id, deleted_at=None)

    @staticmethod
    async def list_todos(user_id: int) -> List[Todo]:
        """특정 사용자의 Todo 목록 조회 (Soft Delete 제외)"""
        return await Todo.filter(user_id=user_id, deleted_at=None).all()

    @staticmethod
    async def update_todo(todo_id: int, **kwargs) -> Optional[Todo]:
        """Todo 업데이트"""
        todo = await Todo.get_or_none(id=todo_id, deleted_at=None)
        if todo:
            for field, value in kwargs.items():
                setattr(todo, field, value)
            await todo.save()
        return todo

    @staticmethod
    async def soft_delete_todo(todo_id: int) -> Optional[Todo]:
        """Soft Delete (deleted_at만 기록)"""
        todo = await Todo.get_or_none(id=todo_id, deleted_at=None)
        if todo:
            todo.deleted_at = datetime.utcnow()
            await todo.save()
        return todo

    @staticmethod
    async def hard_delete_todo(todo_id: int) -> int:
        """실제 DB에서 삭제 (필요 시만 사용)"""
        return await Todo.filter(id=todo_id).delete()
