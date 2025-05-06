from tortoise import Model, fields


# Модель для хранения услуг салона красоты.
class Service(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField()
    price = fields.FloatField()
    duration = fields.IntField()  # Длительность в минутах

    slots: fields.ReverseRelation["Slot"]  # type: ignore
