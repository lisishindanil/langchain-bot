from tortoise import Model, fields

from app.database.service import Service
from app.database.master import Master


# Модель для хранения временных слотов (доступных записей).
class Slot(Model):
    id = fields.IntField(pk=True)
    date = fields.DateField()
    time = fields.TimeField()
    status = fields.CharField(max_length=20, default="available")  # available/booked

    service = fields.ForeignKeyField("models.Service", related_name="slots")
    master = fields.ForeignKeyField("models.Master", related_name="slots")

    appointment: fields.ReverseRelation["Appointment"]  # type: ignore
