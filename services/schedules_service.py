from typing import List, Optional
from repositories.schedules_repo import ScheduleRepository
from models.schedules import Schedule


class ScheduleService:
    """
    Service layer for managing Schedules (CRUD).
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
    ) -> Schedule:
        return await ScheduleRepository.create_schedule(
            user_id=user_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            all_day=all_day,
            location=location,
        )

    # ✅ Read (단일 일정 조회 - todos까지 prefetch)
    @staticmethod
    async def get_schedule_by_id(schedule_id: int) -> Optional[Schedule]:
        schedule = await ScheduleRepository.get_schedule_by_id(schedule_id)
        if schedule:
            await schedule.fetch_related("todos")  # ✅ todos 미리 로드
        return schedule

    # ✅ Read (사용자별 일정 목록 조회 - todos까지 prefetch)
    @staticmethod
    async def get_schedules_by_user(user_id: int) -> List[Schedule]:
        schedules = await ScheduleRepository.get_schedules_by_user(user_id)
        for s in schedules:
            await s.fetch_related("todos")  # ✅ todos 미리 로드
        return schedules

    # ✅ Update
    @staticmethod
    async def update_schedule(schedule_id: int, **kwargs) -> Optional[Schedule]:
        updated = await ScheduleRepository.update_schedule(schedule_id, **kwargs)
        if updated:
            await updated.fetch_related("todos")  # ✅ 업데이트 후에도 todos 로드
        return updated

    # ✅ Delete (소프트 삭제)
    @staticmethod
    async def delete_schedule(schedule_id: int) -> bool:
        return await ScheduleRepository.delete_schedule(schedule_id)
