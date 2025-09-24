from typing import Optional, List
from datetime import datetime
from schemas.schedules import (
    ScheduleCreateRequest,
    ScheduleCreateResponse,
    ScheduleOut,
    ScheduleUpdateRequest,
    ScheduleUpdateResponse,
    ScheduleDeleteResponse,
    ScheduleListResponse,
)
from repositories.schedules_repo import ScheduleRepository
from models.schedules import Schedule


class ScheduleService:
    """
    Service layer for managing schedules (CRUD + soft/hard delete).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_schedule(data: ScheduleCreateRequest) -> ScheduleCreateResponse:
        schedule: Schedule = await ScheduleRepository.create_schedule(
            user_id=data.user_id,
            title=data.title,
            start_time=data.start_time,
            end_time=data.end_time,
            description=data.description,
            location=data.location,
            all_day=data.all_day,
            is_recurring=data.is_recurring,
            recurrence_rule=data.recurrence_rule,
            parent_schedule_id=data.parent_schedule_id,
        )
        return ScheduleCreateResponse.model_validate(schedule, from_attributes=True)

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_schedule_by_id(schedule_id: int) -> Optional[ScheduleOut]:
        schedule: Optional[Schedule] = await ScheduleRepository.get_schedule_by_id(schedule_id)
        if not schedule:
            return None
        return ScheduleOut.model_validate(schedule, from_attributes=True)

    @staticmethod
    async def get_schedules_by_user(user_id: int) -> ScheduleListResponse:
        schedules: List[Schedule] = await ScheduleRepository.get_schedules_by_user(user_id)
        return ScheduleListResponse(
            schedules=[ScheduleOut.model_validate(s, from_attributes=True) for s in schedules],
            total=len(schedules),
        )

    @staticmethod
    async def get_schedules_by_date(user_id: int, date: datetime) -> ScheduleListResponse:
        schedules: List[Schedule] = await ScheduleRepository.get_schedules_by_date(user_id, date)
        return ScheduleListResponse(
            schedules=[ScheduleOut.model_validate(s, from_attributes=True) for s in schedules],
            total=len(schedules),
        )

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_schedule(schedule_id: int, data: ScheduleUpdateRequest) -> Optional[ScheduleUpdateResponse]:
        updated: Optional[Schedule] = await ScheduleRepository.update_schedule(
            schedule_id,
            title=data.title,
            description=data.description,
            start_time=data.start_time,
            end_time=data.end_time,
            location=data.location,
            all_day=data.all_day,
            is_recurring=data.is_recurring,
            recurrence_rule=data.recurrence_rule,
        )
        if not updated:
            return None
        return ScheduleUpdateResponse.model_validate(updated, from_attributes=True)

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_schedule(schedule_id: int, hard: bool = False) -> Optional[ScheduleDeleteResponse]:
        if hard:
            deleted_count: int = await ScheduleRepository.hard_delete_schedule(schedule_id)
            if deleted_count == 0:
                return None
        else:
            success: bool = await ScheduleRepository.delete_schedule(schedule_id)
            if not success:
                return None

        return ScheduleDeleteResponse(message="Schedule deleted successfully")
