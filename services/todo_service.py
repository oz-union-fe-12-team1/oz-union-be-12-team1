from typing import Optional, List
from schemas.todos import (
    TodoCreateRequest,
    TodoCreateResponse,
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
    async def create_todo(data: TodoCreateRequest, user_id: int) -> TodoCreateResponse:
        """
        user_id는 인증 컨텍스트에서 따로 전달받음 (스키마에서 빼고 서비스에서 인자로 받음).
        """
        todo: Todo = await TodosRepository.create_todo(
            user_id=user_id,
            title=data.title,
            description=data.description,
            schedule_id=data.schedule_id,
        )
        return TodoCreateResponse.model_validate(todo, from_attributes=True)

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_todo_by_id(todo_id: int) -> Optional[TodoCreateResponse]:
        todo: Optional[Todo] = await TodosRepository.get_todo_by_id(todo_id)
        if not todo:
            return None
        return TodoCreateResponse.model_validate(todo, from_attributes=True)

    @staticmethod
    async def get_todos_by_user(user_id: int) -> TodoListResponse:
        todos: List[Todo] = await TodosRepository.get_todos_by_user(user_id)
        return TodoListResponse(
            todos=[TodoCreateResponse.model_validate(t, from_attributes=True) for t in todos],
            total=len(todos),
        )

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_todo(
        todo_id: int, data: TodoUpdateRequest
    ) -> Optional[TodoUpdateResponse]:
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
    async def delete_todo(
        todo_id: int, hard: bool = False
    ) -> Optional[TodoDeleteResponse]:
        if hard:
            deleted_count: int = await TodosRepository.hard_delete_todo(todo_id)
            if deleted_count == 0:
                return None
        else:
            success: bool = await TodosRepository.delete_todo(todo_id)
            if not success:
                return None

        return TodoDeleteResponse(message="Todo deleted successfully")
