# Middleware - технология в Mubble, которая позволяет обрабатывать данные до или после их обработки хендлерами.
# Смысл в том, что мы создаем свой класс, основываясь на ABCMiddleware, и реализуем в нем методы pre и post.

# pre - метод, который срабатывает до обработки хендлерами
# post - метод, который срабатывает после обработки хендлерами

from mubble import ABCMiddleware, Dispatch, Message
from mubble.bot.dispatch.context import Context

from app.database.chat_history import ChatHistory
from app.database.user import User


dp = Dispatch()


# Декоратор, который регистрирует Middleware для сообщений
@dp.message.register_middleware()
class MessageContextMiddleware(ABCMiddleware[Message]):
    async def pre(
        self, event: Message, ctx: Context
    ) -> bool:  # Этот метод срабатывает до обработки хендлерами
        user = await User.get_or_none(
            uid=event.from_user.id
        )  # Получаем пользователя из базы данных или None

        if user is None:  # Если пользователя нет в базе данных
            chat_history = await ChatHistory.create()  # Создается новая история чата

            user = await User.create(
                uid=event.from_user.id,
                name=event.from_user.first_name,
                chat_history=chat_history,
                phone=None,
            )
        else:  # Если пользователь уже зарегистрирован
            chat_history = (
                await user.chat_history.first()
            )  # Получаем историю чата пользователя

        # Здесь мы устанавливаем данные для хендлеров в контекст.
        # Это нужно, чтобы было удобно получать эти же данные прям в хендлерах,
        # чтобы в каждом из них не делать запрос к базе данных на получение данных пользователя и истории чата.
        ctx.set("user", user)
        ctx.set("chat_history", chat_history)
        return True  # Возвращаем True, чтобы хендлеры работали дальше, если False, то хендлеры не будут работать
