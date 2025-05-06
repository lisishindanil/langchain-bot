from pathlib import Path

from envparse import env
from mubble import API, ParseMode, Token, logger
from tortoise import Tortoise

from app.database.system import System
from app.database.service import Service
from app.database.master import Master
from app.database.slot import Slot


current_dir = Path(__file__).parent
env.read_envfile(".env")

OPENAI_TOKEN = env.str("OPENAI_TOKEN")  # Токен для OpenAI API

# Настройки базы данных
MODELS_PATH = "app.database"  # Путь к моделям базы данных
models = [
    MODELS_PATH + ".user",  # Модель пользователя
    MODELS_PATH + ".chat_history",  # Модель истории чата
    MODELS_PATH + ".system",  # Модель системы
    MODELS_PATH + ".service",  # Модель услуги
    MODELS_PATH + ".master",  # Модель мастера
    MODELS_PATH + ".slot",  # Модель временного слота
    MODELS_PATH + ".appointment",  # Модель записи клиента
]

TORTOISE_ORM = {
    # Подключение к базе данных (Здесь стоит sqlite3 в файле database.sqlite3, но можно использовать любую другую)
    # Для тестов можно использовать: `sqlite3://:memory:` (База данных будет храниться в памяти)
    # Для asyncpg: `asyncpg://user:password@localhost:5432/database`
    # Для psycopg: `psycopg://user:password@localhost:5432/database`
    # Для mssql: `mysql://user:password@localhost:3306/database?driver=some odbc driver`
    # Подробнее: https://tortoise.github.io/databases.html#clean-familiar-python-interface
    "connections": {"default": "sqlite://database.sqlite3"},
    "apps": {
        "models": {
            "models": models,
            "default_connection": "default",
        }
    },
}


# Функция для инициализации базы данных
async def setup_database() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    if await System.get_or_none(id=1) is None:
        await System.create()

    if not await Service.exists():
        # Услуги
        manicure = await Service.create(
            name="Маникюр",
            description="Догляд за нігтями та руками",
            price=300,
            duration=60,
        )
        pedicure = await Service.create(
            name="Педикюр",
            description="Догляд за стопами та нігтями ніг",
            price=400,
            duration=80,
        )
        facial = await Service.create(
            name="Чистка обличчя",
            description="Професійна чистка шкіри обличчя",
            price=500,
            duration=90,
        )
        brow = await Service.create(
            name="Корекція брів",
            description="Форма та фарбування брів",
            price=250,
            duration=40,
        )
        lash = await Service.create(
            name="Ламінування вій",
            description="Догляд та підкручування вій",
            price=350,
            duration=50,
        )
        massage = await Service.create(
            name="Масаж обличчя",
            description="Розслабляючий масаж для шкіри обличчя",
            price=600,
            duration=60,
        )
        waxing = await Service.create(
            name="Воскова епіляція",
            description="Видалення небажаного волосся воском",
            price=450,
            duration=45,
        )
        spa = await Service.create(
            name="СПА-догляд для рук",
            description="Комплексний догляд для шкіри рук",
            price=550,
            duration=70,
        )

        # Мастера
        elena = await Master.create(name="Олена", specialization="Манікюр, Педикюр")
        irina = await Master.create(
            name="Ірина", specialization="Педикюр, Чистка обличчя"
        )
        anna = await Master.create(
            name="Анна", specialization="Манікюр, Чистка обличчя, СПА-догляд"
        )
        maria = await Master.create(
            name="Марія", specialization="Брови, Вії, Воскова епіляція"
        )
        viktoria = await Master.create(
            name="Вікторія", specialization="Масаж обличчя, СПА-догляд"
        )
        diana = await Master.create(name="Діана", specialization="Манікюр, Брови, Вії")
        olga = await Master.create(
            name="Ольга", specialization="Педикюр, Воскова епіляція"
        )
        svetlana = await Master.create(
            name="Світлана", specialization="СПА-догляд, Масаж обличчя"
        )

        # Слоты (на сегодня)
        from datetime import date, time

        await Slot.create(
            date=date.today(),
            time=time(9, 0),
            status="available",
            service=manicure,
            master=elena,
        )
        await Slot.create(
            date=date.today(),
            time=time(10, 0),
            status="available",
            service=pedicure,
            master=irina,
        )
        await Slot.create(
            date=date.today(),
            time=time(11, 0),
            status="available",
            service=facial,
            master=anna,
        )
        await Slot.create(
            date=date.today(),
            time=time(12, 0),
            status="available",
            service=brow,
            master=maria,
        )
        await Slot.create(
            date=date.today(),
            time=time(13, 0),
            status="available",
            service=lash,
            master=diana,
        )
        await Slot.create(
            date=date.today(),
            time=time(14, 0),
            status="available",
            service=massage,
            master=viktoria,
        )
        await Slot.create(
            date=date.today(),
            time=time(15, 0),
            status="available",
            service=waxing,
            master=olga,
        )
        await Slot.create(
            date=date.today(),
            time=time(16, 0),
            status="available",
            service=spa,
            master=svetlana,
        )
        await Slot.create(
            date=date.today(),
            time=time(17, 0),
            status="available",
            service=manicure,
            master=diana,
        )
        await Slot.create(
            date=date.today(),
            time=time(18, 0),
            status="available",
            service=facial,
            master=anna,
        )

    Tortoise.init_models(models, "models")


# Настройки бота
# Устанавливаем уровень логирования: он не блокирует поток, это лучше чем использование print
logger.set_level(
    "DEBUG"
)  # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "EXCEPTION"
# .from_env() - функция, которая автоматически сканирует .env на наличие переменной BOT_TOKEN
api = API(Token.from_env(path_to_envfile=".env"))
# Устанавливаем режим парсинга всех сообщений в HTML (чтобы можно было делать форматирование текста)
api.default_params["parse_mode"] = ParseMode.HTML

MAX_MESSAGES = 30  # Максимальное количество сообщений в истории чата
MAX_TOKENS = 50000  # Максимальное количество токенов в истории чата
LLM_MODEL = "gpt-4o"  # Модель, которая используется в проекте
