from typing import List, Optional
from repositories.todos_repo import TodosRepository
from models.todo import Todo


class TodoService:
    """
    Service layer for managing Todos (CRUD).
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
        """새로운 Todo 생성"""
        return await TodosRepository.create_todo(
            user_id=user_id,
            title=title,
            description=description,
            schedule_id=schedule_id,
        )

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_todo_by_id(todo_id: int) -> Optional[Todo]:
        """ID 기준 단일 Todo 조회"""
        todo = await TodosRepository.get_todo_by_id(todo_id)
        return todo

    @staticmethod
    async def get_todos_by_user(user_id: int) -> List[Todo]:
        """특정 사용자의 Todo 목록 조회"""
        todos = await TodosRepository.get_todos_by_user(user_id)
        return todos

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_todo(
        todo_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_completed: Optional[bool] = None,
        schedule_id: Optional[int] = None,
    ) -> Optional[Todo]:
        """Todo 수정"""
        update_fields = {
            "title": title,
            "description": description,
            "is_completed": is_completed,   # ✅ 스키마에서 체크박스 방식이므로 그대로 유지
            "schedule_id": schedule_id,
        }
        # ✅ None 값은 무시하고 실제 수정할 값만 전달
        update_fields = {k: v for k, v in update_fields.items() if v is not None}

        updated = await TodosRepository.update_todo(todo_id, **update_fields)
        return updated

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_todo(todo_id: int) -> bool:
        """Todo 소프트 삭제"""
        return await TodosRepository.delete_todo(todo_id)
