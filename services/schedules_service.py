from datetime import datetime, timedelta, timezone
from typing import List, Optional, Any

from repositories.schedules_repo import ScheduleRepository
from schemas.schedules import ScheduleOut


# ✅ 한국 표준시 (KST) 설정
KST = timezone(timedelta(hours=9))


class ScheduleService:
    """
    Service layer for managing Schedules (CRUD + soft/hard delete).
    """

    # ==========================================================
    # 🧩 1️⃣ Create
    # ==========================================================
    @staticmethod
    async def create_schedule(**kwargs: Any) -> ScheduleOut:
        """
        일정 생성 시, start_time / end_time 이 한국시간(KST)으로 들어오면
        DB 저장 전에 UTC로 변환해서 저장.
        """
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")

        # ✅ start_time과 end_time이 datetime이면 UTC로 변환
        if isinstance(start_time, datetime):
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=KST)
            kwargs["start_time"] = start_time.astimezone(timezone.utc)

        if isinstance(end_time, datetime):
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=KST)
            kwargs["end_time"] = end_time.astimezone(timezone.utc)

        schedule = await ScheduleRepository.create_schedule(**kwargs)
        return ScheduleOut.model_validate(schedule, from_attributes=True)

    # ==========================================================
    # 🧩 2️⃣ Read (단일 일정 조회)
    # ==========================================================
    @staticmethod
    async def get_schedule_by_id(schedule_id: int) -> Optional[ScheduleOut]:
        schedule = await ScheduleRepository.get_schedule_by_id(schedule_id)
        if not schedule:
            return None

        # ✅ UTC → KST 변환 후 반환
        schedule.start_time = schedule.start_time.astimezone(KST)
        schedule.end_time = schedule.end_time.astimezone(KST)

        return ScheduleOut.model_validate(schedule, from_attributes=True)

    # ==========================================================
    # 🧩 3️⃣ Read (사용자별 일정 목록)
    # ==========================================================
    @staticmethod
    async def get_schedules_by_user(user_id: int) -> List[ScheduleOut]:
        schedules = await ScheduleRepository.get_schedules_by_user(user_id)

        # ✅ 전체 일정 UTC → KST 변환 후 반환
        for s in schedules:
            if s.start_time:
                s.start_time = s.start_time.astimezone(KST)
            if s.end_time:
                s.end_time = s.end_time.astimezone(KST)

        return [ScheduleOut.model_validate(s, from_attributes=True) for s in schedules]

    # ==========================================================
    # 🧩 4️⃣ Update
    # ==========================================================
    @staticmethod
    async def update_schedule(schedule_id: int, **kwargs: Any) -> Optional[ScheduleOut]:
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")

        # ✅ 업데이트 시에도 변환 처리
        if isinstance(start_time, datetime):
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=KST)
            kwargs["start_time"] = start_time.astimezone(timezone.utc)

        if isinstance(end_time, datetime):
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=KST)
            kwargs["end_time"] = end_time.astimezone(timezone.utc)

        updated = await ScheduleRepository.update_schedule(schedule_id, **kwargs)
        if not updated:
            return None

        # ✅ UTC → KST 변환 후 반환
        updated.start_time = updated.start_time.astimezone(KST)
        updated.end_time = updated.end_time.astimezone(KST)

        return ScheduleOut.model_validate(updated, from_attributes=True)

    # ==========================================================
    # 🧩 5️⃣ Delete (soft/hard 분기)
    # ==========================================================
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
