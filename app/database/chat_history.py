from tortoise import Model, fields

from app.database.user import User
from app.llm.prompts import entry


# Модель для хранения истории чата.
# У неё связь OnetoOne с моделью User, чтобы можно было получить историю чата по пользователю.
# В поле user описана обратная связь с помощью типизации.
class ChatHistory(Model):
    id = fields.IntField(pk=True)  # ID истории чата
    data = fields.JSONField(
        default=[{"role": "system", "content": entry}], null=True
    )  # Данные истории чата (по умолчанию записывается изначальный промпт)
    last_update = fields.DatetimeField(
        auto_now=True
    )  # Время последнего обновления истории чата (автоматически обновляется при сохранении)

    user: fields.ReverseRelation["User"]  # Обратная связь с моделью User

    @property
    def data_length(self) -> int:
        return len(self.data)
