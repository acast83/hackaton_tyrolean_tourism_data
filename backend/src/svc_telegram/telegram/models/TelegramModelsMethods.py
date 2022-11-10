from __future__ import annotations

import datetime
import io
import typing
from enum import Enum
from typing import List, Optional, Union, TypeVar

from pydantic import BaseModel
from .TelegramModelsTypes import *

InputFile = TypeVar('InputFile', io.BytesIO, io.FileIO, str)


__all__ = [
    "SendMessage",
    "ObjectForTelegramWorker",
    "MessageEncodeTypes",
]


class MessageEncodeTypes(str, Enum):
    sendMessage = 'sendMessage'
    textMessage = 'sendMessage'
    Message = 'sendMessage'


class SendMessage(BaseModel):
    chat_id: Union[int, str]
    text: str
    parse_mode: str = None
    entities: list[MessageEntity] = None
    disable_web_page_preview: bool = None
    disable_notification: bool = None
    protect_content: bool = None
    reply_to_message_id: int = None
    allow_sending_without_reply: bool = None
    reply_markup: Union[InlineKeyboardMarkup,
                        ReplyKeyboardMarkup,
                        ReplyKeyboardRemove,
                        ForceReply] = None


SendMessage.update_forward_refs()


class ObjectForTelegramWorker(BaseModel):
    content_type: str = MessageEncodeTypes.textMessage
    content: typing.Union[
        SendMessage
    ]


ObjectForTelegramWorker.update_forward_refs()
