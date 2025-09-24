from typing import List, Optional
from repositories.todos_repo import TodosRepository
from schemas.todos import TodoOut
from models.todo import Todo


class TodoService:
    """
    Service layer for managing Todos (CRUD + soft delete).
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
    ) -> TodoOut:
        """
        새로운 Todo 생성
        - schedule_id가 있으면 해당 일정에 연결
        - schedule_id가 None이면 독립 Todo로 생성
        """
        todo: Todo = await TodosRepository.create_todo(
            user_id=user_id,
            title=title,
            description=description,
            schedule_id=schedule_id,
        )
        return TodoOut.model_validate(todo, from_attributes=True)

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_todo_by_id(todo_id: int) -> Optional[TodoOut]:
        """ID 기준 단일 Todo 조회 (Soft Delete 제외)"""
        todo = await TodosRepository.get_todo_by_id(todo_id)
        if not todo:
            return None
        return TodoOut.model_validate(todo, from_attributes=True)

    @staticmethod
    async def get_todos_by_user(user_id: int) -> List[TodoOut]:
        """특정 사용자의 Todo 목록 조회 (Soft Delete 제외)"""
        todos = await TodosRepository.get_todos_by_user(user_id)
        return [TodoOut.model_validate(t, from_attributes=True) for t in todos]

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_todo(todo_id: int, **kwargs) -> Optional[TodoOut]:
        """
        Todo 업데이트
        - kwargs: title, description, is_completed, schedule_id 등
        - schedule_id=None → 일정과의 연결 해제
        """
        updated = await TodosRepository.update_todo(todo_id, **kwargs)
        if not updated:
            return None
        return TodoOut.model_validate(updated, from_attributes=True)

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_todo(todo_id: int) -> bool:
        """
        Soft Delete (deleted_at만 기록)
        - 실제 데이터는 남아있고 복구 가능
        """
        return await TodosRepository.delete_todo(todo_id)

    @staticmethod
    async def hard_delete_todo(todo_id: int) -> int:
        """
        실제 DB에서 삭제 (필요 시만 사용)
        - 되돌릴 수 없음
        """
        return await TodosRepository.hard_delete_todo(todo_id)
