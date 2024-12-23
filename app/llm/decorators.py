def terminate_after_answer(func):
    """
    Декоратор, который нужно использовать для функций,
    после которых не нужно генерировать ответ ассистента
    """
    func._terminate_after_answer = True
    return func
