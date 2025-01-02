from mubble import Dispatch, LoopWrapper, Mubble, logger

from app.config import api, setup_database
from app.database.chat_history import ChatHistory
from app.handlers import dps
from app.database.user import User
from app.llm.prompts import entry
from app.utils.auto_cleaner import clean_chat_history_cool


# LoopWrapper: для работы с асинхронными функциями
loop_wrapper = LoopWrapper()
# Dispatch: для работы с командами (хендлерами)
dispatch = Dispatch()
# Загрузка всех наших команд в основной диспетчер, чтобы они добавились в обработку
dispatch.load_many(*dps)


async def update_entry_prompt():
    """
    Обновление системного промпта у всех пользователей
    """
    users = await User.all()
    for user in users:
        chat_history = await user.chat_history
        chat_history.data[0] = {
            "role": "system",
            "content": entry,
        }

        await chat_history.save()


# Этот декоратор срабатывает при запуске бота
@loop_wrapper.lifespan.on_startup
async def on_startup() -> None:
    # Инициализация базы данных
    logger.info("Database initialization...")
    await setup_database()
    logger.info("Database initialized!")

    # Обновление системного промпта
    logger.info("Updating entry prompt...")
    await update_entry_prompt()
    logger.info("Entry prompt updated!")


# Этот декоратор срабатывает каждых 10 секунд
@loop_wrapper.interval(seconds=10)
async def interval():
    chat_histories = await ChatHistory.all()  # Получаем все истории чатов
    for chat_history in chat_histories:  # Проходимся по каждой истории чата
        await clean_chat_history_cool(chat_history)


bot = Mubble(
    api=api,
    dispatch=dispatch,
    loop_wrapper=loop_wrapper,
)

bot.run_forever()
