import os
import uuid
import json
import redis

import base3.handlers
from base3 import http
from base3.core import Base
from base3.decorators import route, api
import tshared.ipc.tenants as ipc_tenants

from .. import models
from ..models.TelegramModelsTypes import *
from ..models.TelegramModelsMethods import *
from ..controllers.TelegramDispatcher import dp
from ..controllers.RedisDispatcher import send_to

db_connection = 'conn_telegram'

BOT_NAME = os.environ.get('TELEGRAM_BOT_NAME')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN or not BOT_NAME:
    print(f'TELEGRAM_BOT_NAME:  |{BOT_NAME}|')
    print(f'TELEGRAM_TOKEN:     |{TELEGRAM_TOKEN}|')
    raise ValueError('Some variable was not set.')

TELEGRAM_BOT_URL = f'https://t.me/{BOT_NAME}'
TELEGRAM_URL_METHOD = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{{}}"


def printd(*args, **kwargs):
    if len(args) == 1 and isinstance(args[0], dict):
        try:
            print(json.dumps(args[0], indent=2), **kwargs)
        except Exception as e:
            kwargs['sep'] = kwargs.get('sep', '\n')
            print(*[f'{k}: {v}' for k, v in args[0].items()], **kwargs)
    else:
        print(*args, **kwargs)


@route('/about')
class TelegramAboutHandler(Base):

    @api(auth=False)
    async def get(self):
        return {'service': 'telegram'}


@route('/options')
class TelegramOptionsHandler(base3.handlers.BaseOptionsHandler):
    model_Option = models.Option
    db_connection = db_connection


@route('/get_update')
class TelegramGetUpdate(base3.handlers.Base):

    @api(auth=False)
    async def post(self, update: dict = None):
        """
        Endpoint for telegram server to send updates to.
        """

        print("POST")
        body = self.request_body()

        if body.get('update_id'):
            update = Update(**body)
            await dp.process_update(update=update, route=self)
            return http.status.OK
        else:
            keys = update.keys() if hasattr(update, 'keys') else {}
            raise http.HttpInvalidParam(id_message="BODY_FORMAT_ERROR",
                                        message=f'Update body does not have "update_id" or '
                                                f'"message" keys: {keys}')


# @route('/find_user_by_uuid_and_tenant_code/:unique_id_and_tenant_code')
# class FindUserByCodeAndTenantHandlerUsingTelegramSVC(base3.handlers.Base):
#
#     @api()
#     async def get(self, unique_id_and_tenant_code: str):
#
#         # this is not good because we can not read users of another tenants,
#         # right place for this is tenant svc and to be unauthorized
#
#
#         from tshared.lookups.cache import LookupUsers, LookupTenants
#         lookup_users = await LookupUsers.create(self)
#         lookup_tenants = await LookupTenants.create(self)
#
#         unique_id, tenant_code = unique_id_and_tenant_code.split(':')
#
#         tenant = lookup_tenants.get(tenant_code, index='code')['id']
#
#         user_id = lookup_users.get(unique_id, index='unique_id')['id']
#
#         return {'id': user_id}
#
#         my_tenant = lookup_tenants.get(self.id_tenant)


@route('/link')
class TelegramLink(base3.handlers.Base):

    @api()
    async def get(self):
        """
        Links users telegram account with systems account.

        Responses:
            200:
                {
                    "link": "t.me/name_of_a_bot?start=ABCDEF-DCUBE"
                }
            401:
                {
                    "method": "GET",
                    "uri": "/api/v3/telegram/link",
                    "code": 401,
                    "id_message": "UNAUTHORIZED",
                    "message": "Unauthorized"
                }
        """

        from tshared.lookups.cache import LookupUsers, LookupTenants
        lookup_users = await LookupUsers.create(self)
        try:
            lookup_tenants = await LookupTenants.create(self)
        except Exception as e:
            raise

        me = lookup_users.get(self.id_user)

        my_tenant = lookup_tenants.get(self.id_tenant)

        # me_again = lookup_users.get('UXXEAX', index='unique_id')
        # me2_again = lookup_users.get('system', index='username')
        # igor = lookup_users.get('igor.jeremic', index='username')

        return {
            # 'me_again': me_again['id'],
            # 'me_id': self.id_user,
            # 'me2_again': me2_again['id'],
            # 'igor': igor['id'],

            'link': f'{TELEGRAM_BOT_URL}?start={me["unique_id"]}--{my_tenant["code"]}'
        }


@route('/send_message/:user_id')
class TelegramSendMessage(base3.handlers.Base):
    """
    Parameters:
        user_id: users id
            type: uuid
            example: 123e4567-e89b-12d3-a456-426614174000
    """

    @api()
    async def post(self, user_id: uuid.UUID,
                   text: str, parse_mode: str = None, disable_web_page_preview: bool = None,
                   disable_notification: bool = None, protect_content: bool = None
                   ):
        """
        Method to send messages via telegram API.
        User should be registered via API/telegram/link.

        Parameters:
            text (body): Text of the message to be sent, 1-4096 characters after entities parsing
            parse_mode (body): Mode for parsing entities in the message text
                enum: MarkdownV2, HTML, Markdown
            disable_web_page_preview: Disables link previews for links in this message
            disable_notification: Disables link previews for links in this message
            protect_content: Protects the contents of the sent message from forwarding and saving

        RequestBody:
            Supports arguments from sendMessage method of
            telegram bot API (core.telegram.org/bots/api#sendmessage)
            {
                "text": "Text of a message",
                "parse_mode": "MarkdownV2",
                "disable_web_page_preview": false,
                "disable_notification": false,
                "protect_content": false,
                "reply_markup": {"inline_keyboard": [[{"text": "i am a button",
                                                       "url": "https://www.google.com"}]]}
            }
        """

        body = self.request_body()
        user = await models.LinkedAccounts.filter(created_by=user_id).get_or_none()

        if user:
            telegram_id = user.telegram_id
            _ = body.pop('chat_id', None)
            text = body.pop('text', 'Empty message.')

            send_to(telegram_id).message(text=text, **body)
            return {"status": "message sent."}
        else:
            raise http.HttpErrorNotFound(message_id="USER_NOT_FOUND",
                                         message="No linked users found, try register user "
                                                 "by calling /telegram/link")


@route('/send_message_to_me')
class TelegramSendMessageToMyUser(base3.handlers.Base):

    @api()
    async def post(self, text: str,
                   parse_mode: str = None, disable_web_page_preview: bool = None,
                   disable_notification: bool = None, protect_content: bool = None
                   ):
        """
        Sends message to currently singed in user.

        Parameters:
            text (body): Text of the message to be sent, 1-4096 characters after entities parsing
            parse_mode (body): Mode for parsing entities in the message text
                enum: MarkdownV2, HTML, Markdown
            disable_web_page_preview: Disables link previews for links in this message
            disable_notification: Disables link previews for links in this message
            protect_content: Protects the contents of the sent message from forwarding and saving

        RequestBody:
            Supports arguments from sendMessage method of
            telegram bot API (core.telegram.org/bots/api#sendmessage)
            {
                "text": "Text of a message",
                "parse_mode": "MarkdownV2",
                "disable_web_page_preview": false,
                "disable_notification": false,
                "protect_content": false,
                "reply_markup": {"inline_keyboard": [[{"text": "i am a button",
                                                       "url": "https://www.google.com"}]]}
            }
        """

        body = self.request_body()

        user_id = str(self.id_user)

        me = await models.LinkedAccounts.filter(created_by=user_id).get_or_none()
        if me:
            _ = body.pop('chat_id', None)
            text = body.pop('text', 'Empty message.')
            send_to(me.telegram_id).message(text=text, **body)
            return {'ok': True, 'description': 'Message sent.'}
        else:
            raise http.HttpErrorNotFound(message_id="USER_NOT_FOUND", message="USER_NOT_FOUND")
