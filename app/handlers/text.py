from mubble import Dispatch, Message, logger
from mubble.rules import HasText

from app.database.chat_history import ChatHistory
from app.enums import Error, Info
from app.llm.wrapper import make_completion

dp = Dispatch()


# Этот хендлер срабатывает, если сообщение содержит текст
@dp.message(HasText())
async def text_handler(message: Message, chat_history: ChatHistory):
    result = await make_completion(chat_history, message)  # Получаем ответ от модели
    if result is Error.NO_CONTENT_IN_RESPONSE:
        logger.error(result)
        return
    if result is Info.TERMINATE_AFTER_ANSWER:
        logger.debug(result)
        return

    await message.answer(result)
