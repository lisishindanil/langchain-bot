import inspect
from typing import Any
from mubble import AiohttpClient, Message
from mubble.types import InputFile
from aioowm import OWM
import time

from app.config import OWM_TOKEN
from app.llm.decorators import (
    terminate_after_answer,
)  # Декоратор, который нам нужен для замораживания ответа модели


http_client = AiohttpClient()
weather = OWM(OWM_TOKEN)


# Пример синхронной функции
def get_only_time() -> dict[str, str]:
    """
    Функция, которая возвращает локальное время на компьютере.
    """
    return {
        "time": time.strftime("%H:%M:%S", time.localtime())
    }  # Возвращает этот объект, который будет читать LLM для анализа


# Пример асинхронной функции
async def get_full_time() -> dict[str, Any]:
    """
    Функция, которая возвращает текущее время в **Киеве**
    * Год
    * Месяц
    * День
    * Час
    * Минута
    * Секунда
    * Миллисекунда
    * День недели
    * Остальное...
    """
    response = await http_client.request_json(
        "https://www.timeapi.io/api/time/current/zone",
        method="GET",
        params={"timezone": "Europe/Kyiv"},
    )

    return response  # Возвращает этот объект, который будет читать LLM для анализа


# Пример асинхронной функции
async def get_weather(city: str) -> dict[str, Any]:
    """
    Получает информацию о погоде в заданном городе.
    * `city` Город, в котором нужно узнать погоду.
    """
    return (
        await weather.get(city)
    ).model_dump()  # Так как нам возвращается объект PyDantic Model, мы используем метод model_dump() чтобы получить json-представление этого объекта


# Пример функции для отправки рандомного изображения
# Она принимает ответ модели и размер изображения
# Если размер не указан, то используется 400
# А также благодаря декоратору @terminate_after_answer делает так, чтобы
# ответ модели не генерировался после вызова этой функции
@terminate_after_answer
async def send_random_image(
    answer: str, size: int = None, *, message: Message
) -> dict[str, str]:
    try:  # Делаем хендлинг ошибок
        # request_bytes - метод, который делает GET запрос и возвращает всегда байты
        image: bytes = await http_client.request_bytes(
            f"https://picsum.photos/{size if size else 400}"  # Получаем рандомное изображение (если не передан размер, то будет 400)
        )
    except Exception as e:
        return {"error": str(e)}  # Возвращаем ошибку, если она возникла для LLM
    await message.answer_photo(
        InputFile("image.png", image), caption=answer
    )  # Отправляем сообщение пользователю с изображением и ответом модели
    return {"status": "image sent"}  # Пишем, что изображение было отправлено


# Словарь, который содержит все функции из этого файла
# В виде: {"название функции": функция}
# Это нужно для использования в tool_calls
tool_objects = {
    name: func
    for name, func in globals().items()
    if inspect.isfunction(func) and func.__module__ == __name__
}


__all__ = ("tool_objects",)
