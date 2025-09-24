from typing import Optional, List
from datetime import datetime
from schemas.todos import (
    TodoCreateRequest,
    TodoCreateResponse,
    TodoOut,
    TodoUpdateRequest,
    TodoUpdateResponse,
    TodoDeleteResponse,
    TodoListResponse,
)
from repositories.todos_repo import TodosRepository
from models.todo import Todo


class TodoService:
    """
    Service layer for managing Todos (CRUD + soft/hard delete).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_todo(data: TodoCreateRequest) -> TodoCreateResponse:
        todo: Todo = await TodosRepository.create_todo(
            user_id=data.user_id,
            title=data.title,
            description=data.description,
            schedule_id=data.schedule_id,
        )
        return TodoCreateResponse.model_validate(todo, from_attributes=True)

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_todo_by_id(todo_id: int) -> Optional[TodoOut]:
        todo: Optional[Todo] = await TodosRepository.get_todo_by_id(todo_id)
        if not todo:
            return None
        return TodoOut.model_validate(todo, from_attributes=True)

    @staticmethod
    async def get_todos_by_user(user_id: int) -> TodoListResponse:
        todos: List[Todo] = await TodosRepository.get_todos_by_user(user_id)
        return TodoListResponse(
            todos=[TodoOut.model_validate(t, from_attributes=True) for t in todos],
            total=len(todos),
        )

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_todo(todo_id: int, data: TodoUpdateRequest) -> Optional[TodoUpdateResponse]:
        updated: Optional[Todo] = await TodosRepository.update_todo(
            todo_id,
            title=data.title,
            description=data.description,
            is_completed=data.is_completed,
            schedule_id=data.schedule_id,
        )
        if not updated:
            return None
        return TodoUpdateResponse.model_validate(updated, from_attributes=True)

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_todo(todo_id: int, hard: bool = False) -> Optional[TodoDeleteResponse]:
        if hard:
            deleted_count: int = await TodosRepository.hard_delete_todo(todo_id)
            if deleted_count == 0:
                return None
        else:
            success: bool = await TodosRepository.delete_todo(todo_id)
            if not success:
                return None

        return TodoDeleteResponse(message="Todo deleted successfully")
