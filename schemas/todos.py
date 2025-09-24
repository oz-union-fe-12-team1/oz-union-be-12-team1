from typing import Annotated, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# -----------------------------
# 공통 속성
# -----------------------------
class TodoBase(BaseModel):
    title: Annotated[str, Field(example="장보기")]
    description: Optional[str] = Field(default=None, example="우유, 계란, 빵 사오기")
    is_completed: Annotated[bool, Field(default=False, example=False)]  # ✅ 기본값 명확히 지정


# -----------------------------
# 요청(Request)
# -----------------------------
class TodoCreate(TodoBase):
    # ✅ 일정과 연결할 때 사용하는 schedule_id (없으면 독립 Todo)
    schedule_id: Optional[int] = Field(default=None, example=1)


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, example="장보기 (수정됨)")
    description: Optional[str] = Field(default=None, example="계란 대신 두부 사오기")
    is_completed: Optional[bool] = Field(default=None, example=True)  # ✅ 수정 시에만 nullable 허용
    # ✅ 일정 변경 가능 (None이면 일정과 분리하거나 그대로 유지)
    schedule_id: Optional[int] = Field(default=None, example=1)


# -----------------------------
# 응답(Response)
# -----------------------------
class TodoOut(TodoBase):
    id: Annotated[int, Field(example=5)]
    user_id: Annotated[int, Field(example=42)]
    # ✅ 연결된 일정 ID (없을 수도 있음)
    schedule_id: Optional[int] = Field(default=None, example=1)
    created_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]
    updated_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]

    model_config = ConfigDict(from_attributes=True)  # ✅ ORM 변환 허용


class TodoListOut(BaseModel):
    todos: List[TodoOut]
    total: Annotated[int, Field(example=1)]

    model_config = ConfigDict(from_attributes=True)  # ✅ 일관성 확보


class TodoDeleteResponse(BaseModel):
    message: Annotated[str, Field(
        default="Todo deleted successfully",
        example="Todo deleted successfully"
    )]

    model_config = ConfigDict(from_attributes=True)
