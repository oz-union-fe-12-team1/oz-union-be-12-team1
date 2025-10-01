from typing import List, Optional, Any
from repositories.schedules_repo import ScheduleRepository
from schemas.schedules import ScheduleOut


class ScheduleService:
    """
    Service layer for managing Schedules (CRUD + soft/hard delete).
    """

    #  Create
    @staticmethod
    async def create_schedule(**kwargs: Any) -> ScheduleOut:
        schedule = await ScheduleRepository.create_schedule(**kwargs)
        return ScheduleOut.model_validate(schedule, from_attributes=True)

    #  Read (단일 일정 조회)
    @staticmethod
    async def get_schedule_by_id(schedule_id: int) -> Optional[ScheduleOut]:
        schedule = await ScheduleRepository.get_schedule_by_id(schedule_id)
        if not schedule:
            return None
        return ScheduleOut.model_validate(schedule, from_attributes=True)

    # ✅ Read (사용자별 일정 목록)
    @staticmethod
    async def get_schedules_by_user(user_id: int) -> List[ScheduleOut]:
        schedules = await ScheduleRepository.get_schedules_by_user(user_id)
        return [ScheduleOut.model_validate(s, from_attributes=True) for s in schedules]

    #  Update
    @staticmethod
    async def update_schedule(schedule_id: int, **kwargs: Any) -> Optional[ScheduleOut]:
        updated = await ScheduleRepository.update_schedule(schedule_id, **kwargs)
        if not updated:
            return None
        return ScheduleOut.model_validate(updated, from_attributes=True)

    #  Delete (soft/hard 분기)
    @staticmethod
    async def delete_schedule(schedule_id: int, hard: bool = False) -> bool:
        """
        삭제 기능 (soft/hard 분기)
        - hard=False → Soft Delete (deleted_at 기록)
        - hard=True  → Hard Delete (DB에서 완전 삭제)
        """
        if hard:
            deleted_count = await ScheduleRepository.hard_delete_schedule(schedule_id)
            return deleted_count > 0
        return await ScheduleRepository.delete_schedule(schedule_id)
