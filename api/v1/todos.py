from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from models.user import User
from core.security import get_current_user
from services.todo_service import TodoService
from schemas.todos import (
    TodoBase,
    TodoUpdate,
    TodoOut,
    TodoListOut,
    TodoDeleteResponse,
)

router = APIRouter(prefix="/todos", tags=["todos"])


# -----------------------------
# 1. Todo 생성
# -----------------------------
@router.post("", response_model=TodoOut)
async def create_todo(
    request: TodoBase,
    current_user: User = Depends(get_current_user),
) -> TodoOut:
    return await TodoService.create_todo(
        user_id=current_user.id,
        title=request.title,
        description=request.description
    )


# -----------------------------
# 2. 내 Todo 전체 조회
# -----------------------------
@router.get("", response_model=TodoListOut)
async def get_my_todos(current_user: User = Depends(get_current_user)) -> TodoListOut:
    todos = await TodoService.get_todos_by_user(current_user.id)
    return TodoListOut(todos=todos, total=len(todos))


# -----------------------------
# 3. 특정 Todo 조회
# -----------------------------
@router.get("/{todo_id}", response_model=TodoOut)
async def get_todo(todo_id: int, current_user: User = Depends(get_current_user)) -> TodoOut:
    todo = await TodoService.get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="TODO_NOT_FOUND")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")
    return todo


# -----------------------------
# 4. Todo 수정
# -----------------------------
@router.patch("/{todo_id}", response_model=TodoOut)
async def update_todo(
    todo_id: int,
    request: TodoUpdate,
    current_user: User = Depends(get_current_user),
) -> Optional[TodoOut]:
    todo = await TodoService.get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="TODO_NOT_FOUND")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    updated = await TodoService.update_todo(
        todo_id,
        **request.model_dump(exclude_unset=True)  #  v2 방식
    )
    return updated


# -----------------------------
# 5. Todo 삭제 (soft/hard 분기)
# -----------------------------
@router.delete("/{todo_id}", response_model=TodoDeleteResponse)
async def delete_todo(
    todo_id: int,
    hard: bool = Query(False, description="True면 완전 삭제, False면 소프트 삭제"),
    current_user: User = Depends(get_current_user),
) -> TodoDeleteResponse:
    todo = await TodoService.get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="TODO_NOT_FOUND")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    deleted = await TodoService.delete_todo(todo_id, hard=hard)
    if not deleted:
        raise HTTPException(status_code=500, detail="DELETE_FAILED")

    return TodoDeleteResponse(
        message="Todo permanently deleted" if hard else "Todo soft deleted successfully"
    )
