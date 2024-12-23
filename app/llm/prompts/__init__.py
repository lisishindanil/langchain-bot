from pathlib import Path
from enum import Enum

CURRENT_DIR = Path(__file__).parent


# Это Enum, который содержит все возможные типы промптов
class PromptType(Enum):
    ENTRY = "entry.txt"
    # Сюда можно добавить другие типы промптов, если они понадобятся


# Эта функция возвращает содержимое файла промпта по его типу
def get_prompt(prompt_type: PromptType) -> str:
    try:
        with open(CURRENT_DIR / prompt_type.value, encoding="UTF-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Unknown prompt type: {prompt_type}")
    except Exception as e:
        raise Exception(f"Error reading prompt file: {e}")


# В переменной entry содержится содержимое файла entry.txt
entry = get_prompt(PromptType.ENTRY)

# Можно добавить другие промпты, если они понадобятся, используя функцию get_prompt

__all__ = ("PromptType", "get_prompt", "entry")
