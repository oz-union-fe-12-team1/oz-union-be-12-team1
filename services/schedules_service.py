from typing import List, Optional
from repositories.schedules_repo import ScheduleRepository
from schemas.schedules import ScheduleOut


class ScheduleService:
    """
    Service layer for managing Schedules (CRUD).
    """

    # ✅ Create
    @staticmethod
    async def create_schedule(**kwargs) -> ScheduleOut:
        schedule = await ScheduleRepository.create_schedule(**kwargs)
        todos = await schedule.todos.all()  # 👈 리스트 변환
        return ScheduleOut.model_validate(
            {**schedule.__dict__, "todos": todos},
            from_attributes=True,
        )

    # ✅ Read (단일 일정 조회)
    @staticmethod
    async def get_schedule_by_id(schedule_id: int) -> Optional[ScheduleOut]:
        schedule = await ScheduleRepository.get_schedule_by_id(schedule_id)
        if not schedule:
            return None
        await schedule.fetch_related("todos")
        todos = await schedule.todos.all()  # 👈 리스트 변환
        return ScheduleOut.model_validate(
            {**schedule.__dict__, "todos": todos},
            from_attributes=True,
        )

    # ✅ Read (사용자별 일정 목록)
    @staticmethod
    async def get_schedules_by_user(user_id: int) -> List[ScheduleOut]:
        schedules = await ScheduleRepository.get_schedules_by_user(user_id)
        results: List[ScheduleOut] = []
        for s in schedules:
            await s.fetch_related("todos")
            todos = await s.todos.all()  # 👈 리스트 변환
            results.append(
                ScheduleOut.model_validate(
                    {**s.__dict__, "todos": todos},
                    from_attributes=True,
                )
            )
        return results

    # ✅ Update
    @staticmethod
    async def update_schedule(schedule_id: int, **kwargs) -> Optional[ScheduleOut]:
        updated = await ScheduleRepository.update_schedule(schedule_id, **kwargs)
        if not updated:
            return None
        await updated.fetch_related("todos")
        todos = await updated.todos.all()  # 👈 리스트 변환
        return ScheduleOut.model_validate(
            {**updated.__dict__, "todos": todos},
            from_attributes=True,
        )

    # ✅ Delete
    @staticmethod
    async def delete_schedule(schedule_id: int) -> bool:
        return await ScheduleRepository.delete_schedule(schedule_id)
