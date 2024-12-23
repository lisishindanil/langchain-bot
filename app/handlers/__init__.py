from app.handlers import photo
from .middlewares import dps as middleware_dps
from . import photo_caption, text

dps = [*middleware_dps, text.dp, photo_caption.dp, photo.dp]
