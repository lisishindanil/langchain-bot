from typing import Any
from mubble import logger
import tiktoken
import json

from app.config import LLM_MODEL, MAX_MESSAGES, MAX_TOKENS
from app.database.chat_history import ChatHistory


async def clean_chat_history(chat_history: ChatHistory):
    """
    Автоматически удаляет старые сообщения из истории чата, если они превышают лимит по количеству сообщений.

    * `chat_history`: Объект ChatHistory, хранящий историю чата.
    """
    if len(chat_history.data) > MAX_MESSAGES:
        for _ in range(len(chat_history.data) - MAX_MESSAGES):
            try:
                chat_history.data.pop(1)
            except Exception as e:
                logger.error("Failed to delete old messages from chat history.", e)
        await chat_history.save()

        logger.debug(
            "Old messages were deleted from chat history to meet the messages limit. "
        )


async def clean_chat_history_cool(chat_history: ChatHistory):
    # ВАЖНО!!!! ЭТА ШТУКА ПРОСТО ОПТИМИЗАТОР, ОНА СЧИТАЕТ ТОКЕНЫ С ЗАПАСОМ СПЕЦИАЛЬНО!!!
    # НА САМОМ ДЕЛЕ GPT-модели ЖРУТ НЕ ТАК МНОГО ТОКЕНОВ, КАК ТУТ НАПИСАНО!!! ОНИ ЖРУТ В РАЗ 10-20 МЕНЬШЕ!!!!!
    # Не удаляем первое сообщение с ролью "system" (промпт)
    if not chat_history.data or len(chat_history.data) <= 1:
        return

    # Находим все сообщения с ролью "function"
    function_messages_indices = [
        i for i, msg in enumerate(chat_history.data) if msg["role"] == "function"
    ]

    # Оставляем последние три сообщения с ролью "function"
    if len(function_messages_indices) > 3:
        indices_to_delete = function_messages_indices[:-3]
        # Удаляем лишние сообщения с конца, чтобы не нарушать индексы
        for index in sorted(indices_to_delete, reverse=True):
            del chat_history.data[index]

    # Подсчет общего количества токенов в истории чата
    total_tokens = 0
    for message in chat_history.data:
        total_tokens += count_tokens(message)

    # Удаляем самые старые сообщения (кроме первого), пока не уложимся в лимит токенов
    current_index = 1  # начинаем со второго сообщения
    while total_tokens >= MAX_TOKENS and current_index < len(chat_history.data):
        message = chat_history.data[current_index]
        total_tokens -= count_tokens(message)
        del chat_history.data[current_index]
        await chat_history.save()


def count_tokens(message: dict[str, Any], model_name=LLM_MODEL):
    encoding = tiktoken.encoding_for_model(model_name)

    # Проверяем тип контента и сериализуем его в строку, если это dict или list
    content = message["content"]
    if isinstance(content, (dict, list)):
        content = json.dumps(content)

    # Кодируем роль и контент сообщения
    role_tokens = encoding.encode(message["role"])
    content_tokens = encoding.encode(content)

    # Возвращаем общее количество токенов для этого сообщения
    return len(role_tokens) + len(content_tokens)


# Функция для подсчета токенов в сообщении тупая для дебилов
def count_tokens_simple(text: str):
    # Для точного подсчета можно использовать библиотеку tiktoken
    # Здесь для упрощения считаем, что в среднем 1 токен десь 4 символа
    return len(text) // 4
