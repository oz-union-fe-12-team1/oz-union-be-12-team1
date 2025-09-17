from tortoise import fields
from tortoise.models import Model


class Notification(Model):
    id = fields.IntField(pk=True)
    # PK, 자동 증가 정수 ID (알림 고유 ID)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="notifications",
        on_delete=fields.CASCADE,
        null=False
    )
    # FK → 알림을 받을 사용자 (삭제 시 알림도 같이 삭제됨)

    schedule = fields.ForeignKeyField(
        "models.Schedule",
        related_name="notifications",
        null=True,
        on_delete=fields.SET_NULL
    )
    # FK → 관련 일정 (없을 수 있음, 일정이 삭제되면 NULL 처리)

    todo = fields.ForeignKeyField(
        "models.Todo",
        related_name="notifications",
        null=True,
        on_delete=fields.SET_NULL
    )
    # FK → 관련 할 일 (없을 수 있음, 할 일이 삭제되면 NULL 처리)

    message = fields.CharField(max_length=255, null=False)
    # 알림 메시지 (이메일 제목이나 요약 내용)

    notify_at = fields.DatetimeField(null=True)
    # 이메일 발송 예정 시간 (NULL → 예약 발송 없음, 즉시 발송 가능)

    is_read = fields.BooleanField(default=False)
    # 읽음 여부 (인앱 알림 확인용, 이메일 발송만 한다면 DB 기록용)

    created_at = fields.DatetimeField(auto_now_add=True)
    # 레코드 생성 시간 (DEFAULT now())

    updated_at = fields.DatetimeField(auto_now=True)
    # 레코드 수정 시간 (DEFAULT now())

    class Meta:
        table = "notifications"
        # DB 테이블명 고정
