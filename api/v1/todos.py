from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from core.security import get_current_user
from services.todo_service import TodoService
from schemas.todos import (
    TodoCreate,
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
    request: TodoCreate,
    current_user: User = Depends(get_current_user),
):
    todo = await TodoService.create_todo(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        schedule_id=request.schedule_id,
    )
    return TodoOut.from_orm(todo)


# -----------------------------
# 2. 내 Todo 전체 조회
# -----------------------------
@router.get("", response_model=TodoListOut)
async def get_my_todos(current_user: User = Depends(get_current_user)):
    todos = await TodoService.get_todos_by_user(current_user.id)
    return {
        "todos": [TodoOut.from_orm(t) for t in todos],
        "total": len(todos),
    }


# -----------------------------
# 3. 특정 Todo 조회
# -----------------------------
@router.get("/{todo_id}", response_model=TodoOut)
async def get_todo(todo_id: int, current_user: User = Depends(get_current_user)):
    todo = await TodoService.get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="TODO_NOT_FOUND")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")
    return TodoOut.from_orm(todo)


# -----------------------------
# 4. Todo 수정
# -----------------------------
@router.put("/{todo_id}", response_model=TodoOut)
async def update_todo(
    todo_id: int,
    request: TodoUpdate,
    current_user: User = Depends(get_current_user),
):
    todo = await TodoService.get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="TODO_NOT_FOUND")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    # ✅ None 값 제외하고 업데이트
    updated = await TodoService.update_todo(
        todo_id,
        title=request.title,
        description=request.description,
        is_completed=request.is_completed,
        schedule_id=request.schedule_id,
    )
    return TodoOut.from_orm(updated)


# -----------------------------
# 5. Todo 삭제
# -----------------------------
@router.delete("/{todo_id}", response_model=TodoDeleteResponse)
async def delete_todo(todo_id: int, current_user: User = Depends(get_current_user)):
    todo = await TodoService.get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="TODO_NOT_FOUND")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    deleted = await TodoService.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="DELETE_FAILED")

    return {"message": "Todo deleted successfully"}
