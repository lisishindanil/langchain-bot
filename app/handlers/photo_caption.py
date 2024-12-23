from mubble import Dispatch, Message

from app.database.chat_history import ChatHistory
from app.rules import HasPhotoWithCaption


dp = Dispatch()


# Этот хендлер срабатывает, если сообщение содержит фото с подписью
@dp.message(HasPhotoWithCaption())
async def photo_caption_handler(message: Message, chat_history: ChatHistory):
    photo_id = message.photo.unwrap()[-1].file_id  # Получаем ID фото (самое большое фото, так как индекс -1)
    photo_path = (await message.ctx_api.get_file(photo_id)).unwrap().file_path.unwrap()  # Получаем путь к фото
    photo_bytes: bytes = await message.ctx_api.download_file(photo_path)  # Скачиваем фото (получаем байты)

    await message.answer(
        f"Photo received! Size: {len(photo_bytes)} bytes. Caption: {message.caption.unwrap()}"
    )
