from tortoise import fields
from tortoise.models import Model


class Inquiries(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="inquiries",
        on_delete=fields.CASCADE
    )
    title = fields.CharField(max_length=255)
    message = fields.TextField()
    status = fields.CharField(max_length=20, default="pending")
    admin_reply = fields.TextField(null=True)
    replied_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "inquiries"

    def str(self):
        return f"Inquiry(id={self.id}, user={self.user_id}, title={self.title})"

 