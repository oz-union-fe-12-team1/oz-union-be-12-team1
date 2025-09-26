from typing import List, Optional, Any
from tortoise.exceptions import DoesNotExist
from datetime import datetime, timezone
from models.schedules import Schedule


class ScheduleRepository:
    """
    Repository for managing schedules (CRUD + soft delete).
    """

    # --------------------
    # CREATE
    # --------------------
    @staticmethod
    async def create_schedule(
        user_id: int,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        all_day: bool = False,
        is_recurring: bool = False,
        recurrence_rule: Optional[str] = None,
        parent_schedule_id: Optional[int] = None,
    ) -> Schedule:
        """새로운 일정 생성"""
        return await Schedule.create(
            user_id=user_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            all_day=all_day,
        )

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_schedule_by_id(schedule_id: int) -> Optional[Schedule]:
        """ID 기준 단일 일정 조회"""
        return await Schedule.get_or_none(id=schedule_id)

    @staticmethod
    async def get_schedules_by_user(user_id: int) -> List[Schedule]:
        """특정 사용자의 전체 일정 조회"""
        return await Schedule.filter(user_id=user_id)

    @staticmethod
    async def get_schedules_by_date(user_id: int, date: datetime) -> List[Schedule]:
        """특정 날짜의 일정 조회"""
        return await Schedule.filter(
            user_id=user_id,
            deleted_at=None,
            start_time__lte=date,
            end_time__gte=date
        )

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_schedule(schedule_id: int, **kwargs: Any) -> Optional[Schedule]:
        """일정 업데이트"""
        schedule = await Schedule.get_or_none(id=schedule_id)
        if schedule:
            for field, value in kwargs.items():
                if hasattr(schedule, field) and value is not None:
                    setattr(schedule, field, value)
            await schedule.save()
        return schedule

    # --------------------
    # DELETE
    # delete_at = None / soft delete
    # --------------------
    @staticmethod
    async def delete_schedule(schedule_id: int) -> bool:
        """Soft Delete (deleted_at만 기록)"""
        schedule = await Schedule.get_or_none(id=schedule_id)
        if schedule:
            schedule.deleted_at = datetime.now(timezone.utc)  # ✅ UTC 권장
            await schedule.save()
            return True
        return False

    @staticmethod
    async def hard_delete_schedule(schedule_id: int) -> int:
        """실제 DB에서 삭제 (필요 시만 사용)"""
        return await Schedule.filter(id=schedule_id).delete()
