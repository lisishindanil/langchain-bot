import inspect
from typing import Any
from mubble import AiohttpClient, Message
import time

from app.llm.decorators import (
    terminate_after_answer,
)  # Декоратор, который нам нужен для замораживания ответа модели


# Словарь, который содержит все функции из этого файла
# В виде: {"название функции": функция}
# Это нужно для использования в tool_calls
tool_objects = {
    name: func
    for name, func in globals().items()
    if inspect.isfunction(func) and func.__module__ == __name__
}


__all__ = ("tool_objects",)
