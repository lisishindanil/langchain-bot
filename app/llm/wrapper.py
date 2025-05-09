import inspect  # Модуль для работы с функциями (получение аргументов, их значения и т.д.)
import json  # Модуль для работы с JSON, желательно использовать orjson, так как он быстрее
from typing import Any, Callable  # Модуль для работы с типами данных
from datetime import datetime

from mubble import (
    Message,
    logger,
)  # Message - объект сообщения телеграм, logger - модуль для логирования
from langchain_openai import ChatOpenAI
from app.database.chat_history import ChatHistory  # Модель истории чата
from app.config import LLM_MODEL, OPENAI_TOKEN  # Конфигурация
from app.llm import tools, tool_objects  # Инструменты и объекты инструментов
from app.enums import Error, Info  # Перечисления ошибок и информации

client = ChatOpenAI(api_key=OPENAI_TOKEN, model=LLM_MODEL).bind_tools(
    tools=tools, tool_choice="auto"
)  # Клиент для работы с OpenAI API


def get_current_time():
    """
    Повертає поточний час у форматі ISO 8601.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def make_completion(chat_history: ChatHistory, message: Message) -> str | None:
    """
    Обрабатывает сообщение пользователя, создаёт ответ с помощью модели и вызывает необходимые инструменты.
    Все промежуточные сообщения сохраняются во временном списке и обновляются в истории чата только в конце.
    """
    temp_messages = chat_history.data.copy()  # Копируем все сообщения из истории чата
    temp_messages.append(
        {"role": "system", "content": f"Current time and date: {get_current_time()}"}
    )
    temp_messages.append(
        {"role": "user", "content": message.text.unwrap()}
    )  # Добавляем сообщение пользователя

    while (
        True
    ):  # Бесконечный цикл, пока не будет получен ответ от модели и пока она не пройдется по всем цепочкам инструментов
        response = await get_model_text_response(
            temp_messages
        )  # Получаем ответ от модели
        result_message = response.content

        if tool_calls := response.additional_kwargs.get(
            "tool_calls", []
        ):  # Если есть инструменты
            tool_responses, should_terminate = await handle_tool_calls(
                tool_calls, message
            )  # Обрабатываем инструменты
            temp_messages.extend(tool_responses)  # Добавляем результаты инструментов
            if (
                should_terminate
            ):  # Если нужно завершить генерацию ответа после выполнения инструмента
                await save_chat_history(
                    chat_history, temp_messages
                )  # Сохраняем все сообщения
                return Info.TERMINATE_AFTER_ANSWER  # Возвращаем информацию о завершении
            continue  # Пропускаем остальной код
        elif result_message:  # Если есть контент
            temp_messages.append(
                {"role": "assistant", "content": result_message}
            )  # Добавляем контент
            await save_chat_history(
                chat_history, temp_messages
            )  # Сохраняем все сообщения
            return result_message  # Возвращаем контент
        else:
            return Error.NO_CONTENT_IN_RESPONSE  # Возвращаем ошибку


async def get_model_text_response(messages: dict):
    """Получает ответ от модели с заданными сообщениями."""
    return await client.ainvoke(
        input=messages
    )  # Создаём запрос к модели с сообщениями и инструментами


async def handle_tool_calls(tool_calls: list, message: Message) -> list[dict[str, Any]]:
    """Обрабатывает все tool_calls и возвращает список сообщений с результатами выполнения инструментов."""
    temp_tool_messages = []  # Временный список сообщений с результатами инструментов
    should_terminate = False  # Флаг, который показывает, нужно ли завершить генерацию ответа после выполнения инструмента

    for tool_call in tool_calls:  # Проходимся по всем инструментам
        tool_name = tool_call.get("function", {}).get("name")
        tool_args = json.loads(tool_call.get("function", {}).get("arguments", []))

        if tool := tool_objects.get(tool_name):  # Если инструмент существует
            logger.debug(
                "Executing tool: {} with arguments: {}", tool_name, tool_args
            )  # Логируем информацию
            result = await execute_tool(
                tool, tool_args, message
            )  # Выполняем инструмент
            temp_tool_messages.append(
                {
                    "role": "function",
                    "content": json.dumps(result, ensure_ascii=False),
                    "name": tool_name,
                }
            )  # Добавляем результат во временный список
            if getattr(
                tool, "_terminate_after_answer", False
            ):  # Если нужно завершить генерацию ответа после выполнения инструмента
                should_terminate = True  # Устанавливаем флаг

    return (
        temp_tool_messages,
        should_terminate,
    )  # Возвращаем список сообщений с результатами инструментов и флаг завершения


async def execute_tool(tool: Callable, tool_args: dict, message: Any = None) -> Any:
    """Выполняет указанный инструмент с переданными аргументами."""
    signature = inspect.signature(tool)  # Получаем сигнатуру инструмента
    if (
        "message" in signature.parameters and message is not None
    ):  # Если инструмент требует message, передаём его.
        tool_args = {**tool_args, "message": message}

    return (
        await tool(**tool_args)
        if inspect.iscoroutinefunction(tool)
        else tool(**tool_args)
    )  # Выполняем инструмент и возвращаем результат


async def save_chat_history(chat_history: ChatHistory, messages: dict) -> None:
    """Сохраняет все сообщения в истории чата."""
    chat_history.data = messages  # Добавляем сообщения
    await chat_history.save()  # Сохраняем историю чата
