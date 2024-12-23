from tortoise import Model, fields


# Модель для хранения пользователей.
# У неё есть поле chat_history, которое связано с моделью ChatHistory через ForeignKeyField.
class User(Model):
    id = fields.IntField(pk=True)
    # uid (Telegram ID): BigInt, потому что TelegramID выходит за границы 32-bit числа
    uid = fields.BigIntField(unique=True)
    name = fields.CharField(max_length=255)

    chat_history = fields.ForeignKeyField(
        "models.ChatHistory", related_name="user", null=True
    )
