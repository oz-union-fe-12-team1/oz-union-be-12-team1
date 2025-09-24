from typing import List, Optional
from repositories.schedules_repo import ScheduleRepository
from schemas.schedules import ScheduleOut


class ScheduleService:
    """
    Service layer for managing Schedules (CRUD + soft/hard delete).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_schedule(**kwargs) -> ScheduleOut:
        """새로운 일정 생성"""
        schedule = await ScheduleRepository.create_schedule(**kwargs)
        todos = await schedule.todos.all()
        return ScheduleOut.model_validate(
            {**schedule.__dict__, "todos": todos},
            from_attributes=True,
        )

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_schedule_by_id(schedule_id: int) -> Optional[ScheduleOut]:
        """ID 기준 단일 일정 조회 (삭제된 건 제외)"""
        schedule = await ScheduleRepository.get_schedule_by_id(schedule_id)
        if not schedule:
            return None
        await schedule.fetch_related("todos")
        todos = await schedule.todos.all()
        return ScheduleOut.model_validate(
            {**schedule.__dict__, "todos": todos},
            from_attributes=True,
        )

    @staticmethod
    async def get_schedules_by_user(user_id: int) -> List[ScheduleOut]:
        """특정 사용자의 전체 일정 조회 (삭제된 건 제외)"""
        schedules = await ScheduleRepository.get_schedules_by_user(user_id)
        results: List[ScheduleOut] = []
        for s in schedules:
            await s.fetch_related("todos")
            todos = await s.todos.all()
            results.append(
                ScheduleOut.model_validate(
                    {**s.__dict__, "todos": todos},
                    from_attributes=True,
                )
            )
        return results

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_schedule(schedule_id: int, **kwargs) -> Optional[ScheduleOut]:
        """일정 업데이트 (삭제된 건 수정 불가)"""
        updated = await ScheduleRepository.update_schedule(schedule_id, **kwargs)
        if not updated:
            return None
        await updated.fetch_related("todos")
        todos = await updated.todos.all()
        return ScheduleOut.model_validate(
            {**updated.__dict__, "todos": todos},
            from_attributes=True,
        )

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_schedule(schedule_id: int, hard: bool = False) -> bool:
        """
        일정 삭제 (soft/hard 분기)
        - hard=False → Soft Delete (deleted_at 기록)
        - hard=True  → Hard Delete (DB에서 완전 삭제)
        """
        if hard:
            deleted_count = await ScheduleRepository.hard_delete_schedule(schedule_id)
            return deleted_count > 0
        return await ScheduleRepository.delete_schedule(schedule_id)
