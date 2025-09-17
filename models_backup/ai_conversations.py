from tortoise import fields
from tortoise.models import Model


class AIConversation(Model):
    id = fields.BigIntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="ai_conversations",
        on_delete=fields.CASCADE,
        null=False
    )

    session_id = fields.CharField(max_length=255, null=True)

    user_message = fields.TextField(null=True)
    ai_response = fields.TextField(null=True)
    message_type = fields.CharField(max_length=50, null=True)  # user / ai / system

    tokens_used = fields.IntField(null=True)
    response_time_ms = fields.IntField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "ai_conversations"