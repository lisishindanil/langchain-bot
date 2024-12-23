from mubble import Message, MessageRule
from mubble.bot.dispatch.context import Context


# Мы наследуемся от MessageRule и реализуем метод check, который возвращает True, если сообщение содержит фото
class HasPhoto(MessageRule[Message]):
    async def check(self, message: Message, ctx: Context) -> bool:
        return message.photo and message.photo.unwrap()


class HasVoice(MessageRule[Message]):
    async def check(self, message: Message, ctx: Context) -> bool:
        return message.voice and message.voice.unwrap()


class HasPhotoWithCaption(MessageRule[Message]):
    async def check(self, message: Message, ctx: Context) -> bool:
        return (
            message.photo
            and message.photo.unwrap()
            and message.caption
            and message.caption.unwrap()
        )
