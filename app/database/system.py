from tortoise import Model, fields


# Модель для хранения системных данных
class System(Model):
    id = fields.IntField(pk=True)
    reports = fields.JSONField(default=[], null=True)
