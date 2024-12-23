import inspect  # Модуль для работы с функциями (получение аргументов, их значения и т.д.)
import json  # Модуль для работы с JSON, желательно использовать orjson, так как он быстрее
from typing import Any, Callable  # Модуль для работы с типами данных

from mubble import (
    Message,
    logger,
)  # Message - объект сообщения телеграм, logger - модуль для логирования
from openai import AsyncOpenAI  # Клиент для работы с API OpenAI
from openai.types.chat import (
    ChatCompletion,  # Объект ответа модели
    ChatCompletionMessageToolCall,  # Объект инструмента
)
from app.database.chat_history import ChatHistory  # Модель истории чата
from app.config import LLM_MODEL, OPENAI_TOKEN  # Конфигурация
from app.llm import tools, tool_objects  # Инструменты и объекты инструментов
from app.enums import Error, Info  # Перечисления ошибок и информации

client = AsyncOpenAI(
    api_key=OPENAI_TOKEN
)  # Инициализация клиента для работы с API OpenAI


async def make_completion(chat_history: ChatHistory, message: Message) -> str | None:
    """
    Обрабатывает сообщение пользователя, создаёт ответ с помощью модели и вызывает необходимые инструменты.
    Все промежуточные сообщения сохраняются во временном списке и обновляются в истории чата только в конце.
    """
    temp_messages = chat_history.data.copy()  # Копируем все сообщения из истории чата
    temp_messages.append(
        {"role": "user", "content": message.text.unwrap()}
    )  # Добавляем сообщение пользователя

    while (
        True
    ):  # Бесконечный цикл, пока не будет получен ответ от модели и пока она не пройдется по всем цепочкам инструментов
        response = await get_model_text_response(
            temp_messages
        )  # Получаем ответ от модели
        result_message = response.choices[0]  # Получаем ответ

        if tool_calls := result_message.message.tool_calls:  # Если есть инструменты
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
        elif result_content := result_message.message.content:  # Если есть контент
            temp_messages.append(
                {"role": "assistant", "content": result_content}
            )  # Добавляем контент
            await save_chat_history(
                chat_history, temp_messages
            )  # Сохраняем все сообщения
            return result_content  # Возвращаем контент
        else:
            return Error.NO_CONTENT_IN_RESPONSE  # Возвращаем ошибку


async def get_model_text_response(messages: dict) -> ChatCompletion:
    """Получает ответ от модели с заданными сообщениями."""
    return await client.chat.completions.create(
        model=LLM_MODEL, messages=messages, tools=tools
    )  # Создаём запрос к модели с сообщениями и инструментами


async def handle_tool_calls(
    tool_calls: list[ChatCompletionMessageToolCall], message: Message
) -> list[dict[str, Any]]:
    """Обрабатывает все tool_calls и возвращает список сообщений с результатами выполнения инструментов."""
    temp_tool_messages = []  # Временный список сообщений с результатами инструментов
    should_terminate = False  # Флаг, который показывает, нужно ли завершить генерацию ответа после выполнения инструмента

    for tool_call in tool_calls:  # Проходимся по всем инструментам
        tool_name = tool_call.function.name  # Получаем имя инструмента
        tool_args = json.loads(
            tool_call.function.arguments
        )  # Получаем аргументы инструмента

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
