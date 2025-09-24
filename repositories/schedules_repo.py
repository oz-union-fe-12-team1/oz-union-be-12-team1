from typing import List, Optional
from datetime import datetime, timezone
from tortoise.exceptions import DoesNotExist
from models.schedules import Schedule


class ScheduleRepository:
    """
    Repository for managing schedules (CRUD + soft/hard delete).
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
        """
        새로운 일정 생성
        - 기본적으로 반복 옵션(is_recurring, recurrence_rule)은 현재 미사용
        - parent_schedule_id도 확장용 (현재는 null 가능)
        """
        return await Schedule.create(
            user_id=user_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            all_day=all_day,
            is_recurring=is_recurring,
            recurrence_rule=recurrence_rule,
            parent_schedule_id=parent_schedule_id,
        )

    # --------------------
    # READ
    # --------------------
    @staticmethod
    async def get_schedule_by_id(schedule_id: int) -> Optional[Schedule]:
        """ID 기준 단일 일정 조회 (삭제된 건 제외)"""
        return await Schedule.get_or_none(id=schedule_id, deleted_at=None)

    @staticmethod
    async def get_schedules_by_user(user_id: int) -> List[Schedule]:
        """특정 사용자의 전체 일정 조회 (Soft Delete 제외)"""
        return await Schedule.filter(user_id=user_id, deleted_at=None)

    @staticmethod
    async def get_schedules_by_date(user_id: int, date: datetime) -> List[Schedule]:
        """특정 날짜의 일정 조회 (Soft Delete 제외)"""
        return await Schedule.filter(
            user_id=user_id,
            deleted_at=None,
            start_time__lte=date,
            end_time__gte=date,
        )

    # --------------------
    # UPDATE
    # --------------------
    @staticmethod
    async def update_schedule(schedule_id: int, **kwargs) -> Optional[Schedule]:
        """
        일정 업데이트
        - kwargs에 들어온 값만 반영
        - deleted_at != None (즉, 삭제된 일정) 은 업데이트 불가
        """
        schedule = await Schedule.get_or_none(id=schedule_id, deleted_at=None)
        if schedule:
            for field, value in kwargs.items():
                if hasattr(schedule, field) and value is not None:
                    setattr(schedule, field, value)
            await schedule.save()
        return schedule

    # --------------------
    # DELETE
    # --------------------
    @staticmethod
    async def delete_schedule(schedule_id: int) -> bool:
        """
        Soft Delete (deleted_at 기록)
        - 실제 데이터는 남아있음
        """
        schedule = await Schedule.get_or_none(id=schedule_id, deleted_at=None)
        if schedule:
            schedule.deleted_at = datetime.now(timezone.utc)  # ✅ UTC 권장
            await schedule.save()
            return True
        return False

    @staticmethod
    async def hard_delete_schedule(schedule_id: int) -> int:
        """
        Hard Delete (DB에서 완전 삭제)
        - 되돌릴 수 없음
        """
        return await Schedule.filter(id=schedule_id).delete()
