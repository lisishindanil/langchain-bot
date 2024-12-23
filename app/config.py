from pathlib import Path

from envparse import env
from mubble import API, ParseMode, Token, logger
from tortoise import Tortoise

from app.database.system import System


current_dir = Path(__file__).parent
env.read_envfile(".env")

OPENAI_TOKEN = env.str("OPENAI_TOKEN")  # Токен для OpenAI API
OWM_TOKEN = env.str(
    "OWM_TOKEN"
)  # Токен для OpenWeatherMap API (он тут просто для примера)

# Настройки базы данных
MODELS_PATH = "app.database"  # Путь к моделям базы данных
models = [
    MODELS_PATH + ".user",  # Модель пользователя
    MODELS_PATH + ".chat_history",  # Модель истории чата
    MODELS_PATH + ".system",  # Модель системы
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

    Tortoise.init_models(models, "models")


# Настройки бота
# Устанавливаем уровень логирования: он не блокирует поток, это лучше чем использование print
logger.set_level("INFO")  # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "EXCEPTION"
# .from_env() - функция, которая автоматически сканирует .env на наличие переменной BOT_TOKEN
api = API(Token.from_env(path_to_envfile=".env"))
# Устанавливаем режим парсинга всех сообщений в HTML (чтобы можно было делать форматирование текста)
api.default_params["parse_mode"] = ParseMode.HTML

MAX_MESSAGES = 30  # Максимальное количество сообщений в истории чата
MAX_TOKENS = 50000  # Максимальное количество токенов в истории чата
LLM_MODEL = "gpt-4o"  # Модель, которая используется в проекте
