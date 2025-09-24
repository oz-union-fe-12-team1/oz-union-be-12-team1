from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Annotated
from datetime import datetime


# -----------------------------
# 공통 속성
# -----------------------------
class TodoBase(BaseModel):
    title: Annotated[str, Field(example="장보기")]
    description: Annotated[Optional[str], Field(example="우유, 계란, 빵 사오기")] = None
    is_completed: Annotated[bool, Field(example=False)] = False  # ✅ 기본값 False


# -----------------------------
# 요청(Request)
# -----------------------------
class TodoCreateRequest(TodoBase):
    # ✅ 일정과 연결할 때 사용하는 schedule_id (없으면 독립 Todo)
    schedule_id: Annotated[Optional[int], Field(example=1)] = None


class TodoUpdateRequest(BaseModel):
    title: Annotated[Optional[str], Field(example="장보기 (수정됨)")] = None
    description: Annotated[Optional[str], Field(example="계란 대신 두부 사오기")] = None
    is_completed: Annotated[Optional[bool], Field(example=True)] = None
    # ✅ 일정 변경 가능 (None이면 일정과 분리하거나 그대로 유지)
    schedule_id: Annotated[Optional[int], Field(example=1)] = None


# -----------------------------
# 응답(Response)
# -----------------------------
class TodoCreateResponse(TodoBase):
    id: Annotated[int, Field(example=5)]
    user_id: Annotated[int, Field(example=42)]
    schedule_id: Annotated[Optional[int], Field(example=1)] = None
    created_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]
    updated_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]

    model_config = ConfigDict(from_attributes=True)


class TodoUpdateResponse(TodoBase):
    id: Annotated[int, Field(example=5)]
    user_id: Annotated[int, Field(example=42)]
    schedule_id: Annotated[Optional[int], Field(example=1)] = None
    created_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]
    updated_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]

    model_config = ConfigDict(from_attributes=True)


class TodoListResponse(BaseModel):
    todos: List[TodoCreateResponse] = []
    total: Annotated[int, Field(example=1)] = 0

    model_config = ConfigDict(from_attributes=True)


class TodoDeleteResponse(BaseModel):
    message: Annotated[str, Field(example="Todo deleted successfully")] = (
        "Todo deleted successfully"
    )

    model_config = ConfigDict(from_attributes=True)
