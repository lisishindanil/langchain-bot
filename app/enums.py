from enum import StrEnum


class Info(StrEnum):
    TERMINATE_AFTER_ANSWER = (
        "LLM has already answered this question. You cannot answer it again."
    )


class Error(StrEnum):
    NO_CONTENT_IN_RESPONSE = "No content in response"
