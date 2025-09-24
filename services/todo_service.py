from typing import List, Optional
from repositories.todos_repo import TodosRepository
from schemas.todos import TodoOut
from models.todo import Todo


class TodoService:
    """
    Service layer for managing Todos (CRUD + soft/hard delete).
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
        todo = await TodosRepository.get_todo_by_id(todo_id)
        if not todo:
            return None
        return TodoOut.model_validate(todo, from_attributes=True)

    @staticmethod
    async def get_todos_by_user(user_id: int) -> List[TodoOut]:
        todos = await TodosRepository.get_todos_by_user(user_id)
        return [TodoOut.model_validate(t, from_attributes=True) for t in todos]

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_todo(todo_id: int, **kwargs) -> Optional[TodoOut]:
        updated = await TodosRepository.update_todo(todo_id, **kwargs)
        if not updated:
            return None
        return TodoOut.model_validate(updated, from_attributes=True)

    # --------------------
    # DELETE (soft/hard 분기)
    # --------------------
    @staticmethod
    async def delete_todo(todo_id: int, hard: bool = False) -> bool:
        """
        삭제 기능 (soft/hard 분기)
        - hard=False → Soft Delete (deleted_at 기록)
        - hard=True  → Hard Delete (DB에서 완전 삭제)
        """
        if hard:
            deleted_count = await TodosRepository.hard_delete_todo(todo_id)
            return deleted_count > 0
        return await TodosRepository.delete_todo(todo_id)
