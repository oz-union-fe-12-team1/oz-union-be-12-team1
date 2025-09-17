from tortoise import fields
from tortoise.models import Model

class Notification(Model):
    """
    알림(Notification) 모델
    """

    id = fields.IntField(pk=True)  # 알림 고유 ID
    user = fields.ForeignKeyField('models.User', related_name='notifications', on_delete=fields.CASCADE, null=False)  # 사용자 외래키
    schedule = fields.ForeignKeyField('models.Schedule', related_name='notifications', on_delete=fields.SET_NULL, null=True)  # 관련 일정 외래키
    todo = fields.ForeignKeyField('models.Todo', related_name='notifications', on_delete=fields.SET_NULL, null=True)  # 관련 할 일 외래키
    message = fields.CharField(max_length=255, null=False)  # 알림 메시지
    notify_at = fields.DatetimeField(null=True)  # 알림 발송 예정 시간
    is_read = fields.BooleanField(default=False)  # 읽음 여부
    created_at = fields.DatetimeField(auto_now_add=True)  # 생성 시간
    updated_at = fields.DatetimeField(auto_now=True)  # 수정 시간

    class Meta:
        table = "notifications"  # 테이블 명
        ordering = ['-created_at']  # 생성시간 내림차순

    def str(self):
        return f"Notification {self.id} to {self.user.username} - {'Read' if self.is_read else 'Unread'}"
