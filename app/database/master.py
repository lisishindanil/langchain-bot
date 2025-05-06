from tortoise import Model, fields


# Модель для хранения мастеров.
class Master(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    specialization = fields.CharField(max_length=100)

    slots: fields.ReverseRelation["Slot"]  # type: ignore
