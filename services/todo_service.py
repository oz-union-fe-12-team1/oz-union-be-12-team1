from typing import List, Optional
from repositories.todos_repo import TodosRepository  # ✅ _repo로 수정
from models.todo import Todo


class TodoService:
    """
    Service layer for managing Todos (CRUD).
    """

    # ✅ Create
    @staticmethod
    async def create_todo(
        user_id: int,
        title: str,
        description: Optional[str] = None,
        schedule_id: Optional[int] = None
    ) -> Todo:
        return await TodosRepository.create_todo(
            user_id=user_id,
            title=title,
            description=description,
            schedule_id=schedule_id
        )

    # ✅ Read (단일 조회)
    @staticmethod
    async def get_todo_by_id(todo_id: int) -> Optional[Todo]:
        return await TodosRepository.get_todo_by_id(todo_id)

    # ✅ Read (사용자별 투두 목록)
    @staticmethod
    async def get_todos_by_user(user_id: int) -> List[Todo]:
        return await TodosRepository.get_todos_by_user(user_id)

    # ✅ Update
    @staticmethod
    async def update_todo(todo_id: int, **kwargs) -> Optional[Todo]:
        return await TodosRepository.update_todo(todo_id, **kwargs)

    # ✅ Delete (소프트 삭제 → deleted_at 설정)
    @staticmethod
    async def delete_todo(todo_id: int) -> bool:
        return await TodosRepository.delete_todo(todo_id)
