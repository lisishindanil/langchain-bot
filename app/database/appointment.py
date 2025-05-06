from tortoise import Model, fields

from app.database.user import User
from app.database.slot import Slot


# Модель для хранения записей клиентов.
class Appointment(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(max_length=20, default="active")  # active/cancelled

    user = fields.ForeignKeyField("models.User", related_name="appointments")
    slot = fields.ForeignKeyField("models.Slot", related_name="appointment")
