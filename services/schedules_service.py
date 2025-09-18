from typing import List, Optional
from repositories.schedules_repo import ScheduleRepository  # ✅ 단수형으로 수정
from models.schedules import Schedule


class ScheduleService:
    """
    Service layer for managing Schedules (CRUD + 반복 여부/하루 종일 옵션 포함).
    """

    # ✅ Create
    @staticmethod
    async def create_schedule(
        user_id: int,
        title: str,
        start_time,
        end_time,
        description: Optional[str] = None,
        all_day: bool = False,
        location: Optional[str] = None,
        is_recurring: bool = False,
        recurrence_rule: Optional[str] = None,
        parent_schedule_id: Optional[int] = None,
    ) -> Schedule:
        return await ScheduleRepository.create_schedule(
            user_id=user_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            all_day=all_day,
            location=location,
            is_recurring=is_recurring,
            recurrence_rule=recurrence_rule,
            parent_schedule_id=parent_schedule_id,
        )

    # ✅ Read (단일 일정 조회)
    @staticmethod
    async def get_schedule_by_id(schedule_id: int) -> Optional[Schedule]:
        return await ScheduleRepository.get_schedule_by_id(schedule_id)

    # ✅ Read (사용자별 일정 목록 조회)
    @staticmethod
    async def get_schedules_by_user(user_id: int) -> List[Schedule]:
        return await ScheduleRepository.get_schedules_by_user(user_id)

    # ✅ Update (일정 수정)
    @staticmethod
    async def update_schedule(schedule_id: int, **kwargs) -> Optional[Schedule]:
        return await ScheduleRepository.update_schedule(schedule_id, **kwargs)

    # ✅ Delete (소프트 삭제 → deleted_at 설정)
    @staticmethod
    async def delete_schedule(schedule_id: int) -> bool:
        return await ScheduleRepository.delete_schedule(schedule_id)
