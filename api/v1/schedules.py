from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from core.security import get_current_user
from services.schedules_service import ScheduleService
from schemas.schedules import (
    ScheduleCreateRequest,
    ScheduleUpdateRequest,
    ScheduleOut,
    ScheduleListOut,
    ScheduleDeleteResponse,
)

router = APIRouter(prefix="/schedules", tags=["schedules"])


# -----------------------------
# 1. 일정 생성
# -----------------------------
@router.post("", response_model=ScheduleOut)
async def create_schedule(
    request: ScheduleCreateRequest,
    current_user: User = Depends(get_current_user),
):
    schedule = await ScheduleService.create_schedule(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        start_time=request.start_time,
        end_time=request.end_time,
        all_day=request.all_day,
        location=request.location,
    )
    return ScheduleOut.from_orm(schedule)


# -----------------------------
# 2. 내 일정 목록 조회
# -----------------------------
@router.get("/me", response_model=ScheduleListOut)
async def get_my_schedules(current_user: User = Depends(get_current_user)):
    schedules = await ScheduleService.get_schedules_by_user(current_user.id)
    return {
        "schedules": [ScheduleOut.from_orm(s) for s in schedules],
        "total": len(schedules),
    }


# -----------------------------
# 3. 단일 일정 조회
# -----------------------------
@router.get("/{schedule_id}", response_model=ScheduleOut)
async def get_schedule(schedule_id: int, current_user: User = Depends(get_current_user)):
    schedule = await ScheduleService.get_schedule_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="SCHEDULE_NOT_FOUND")

    if schedule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    return ScheduleOut.from_orm(schedule)


# -----------------------------
# 4. 일정 수정
# -----------------------------
@router.put("/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: int,
    request: ScheduleUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    schedule = await ScheduleService.get_schedule_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="SCHEDULE_NOT_FOUND")

    if schedule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    updated = await ScheduleService.update_schedule(schedule_id, **request.dict(exclude_unset=True))
    return ScheduleOut.from_orm(updated)


# -----------------------------
# 5. 일정 삭제
# -----------------------------
@router.delete("/{schedule_id}", response_model=ScheduleDeleteResponse)
async def delete_schedule(schedule_id: int, current_user: User = Depends(get_current_user)):
    schedule = await ScheduleService.get_schedule_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="SCHEDULE_NOT_FOUND")

    if schedule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="NOT_ALLOWED")

    deleted = await ScheduleService.delete_schedule(schedule_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="DELETE_FAILED")

    return {"message": "Schedule deleted successfully"}
