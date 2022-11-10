import uuid
import datetime
from typing import Union

import tshared.models.base as base_models
from tortoise import fields, Model, timezone

from svc_telegram.telegram import models


class Option(Model, base_models.BaseModelOptions):
    class Meta:
        table = "telegram_options"
        unique_together = (('id_tenant', 'key'),)
        app = 'telegram'


class LinkedAccounts(Model, base_models.BaseModel):
    class Meta:
        table = 'telegram_linked_accounts'

    telegram_id = fields.BigIntField(unique=True)


class TelegramMessage(Model, base_models.BaseModel):
    class Meta:
        table = 'telegram_messages'

    receivers_telegram_id = fields.BigIntField()
    message_body = fields.TextField()
    sent = fields.DatetimeField(null=True)
    status = fields.ForeignKeyField('telegram.LookupMessageSendingStatus', null=True, index=True) # return this: False, index=True)
    note = fields.TextField(null=True)

    @classmethod
    async def create_message_and_retry(cls,
                                       receivers_telegram_id: int,
                                       message_body: str,
                                       tenant_id='f0baede9-e55c-426e-9693-fd4d928291e3',
                                       user_id='f0baede9-e55c-426e-9693-fd4d928291e3',
                                       ):
        default_status = await models.LookupMessageSendingStatus.get(code='PENDING')

        message = await cls.create(
            id_tenant=tenant_id,
            created_by=user_id,
            last_updated_by=user_id,

            receivers_telegram_id=receivers_telegram_id,
            message_body=message_body,
            status=default_status,
        )
        await message.save()

        retry = await TelegramMessageRetry.create(message=message)
        await retry.save()

        return message

    async def update_message_success(self):
        """
        * delete retry object
        * update message
            sent = now()
            status = 'SENT'
        """

        retry = await TelegramMessageRetry.get_retry(message_id=self.id)
        await retry.delete()

        status = await models.LookupMessageSendingStatus.get(code='SENT')

        message = await self.update_from_dict(
            {
                'sent': timezone.now(),
                'status': status,
            }
        )
        await message.save()
        return message

    async def update_message_fail(self, note=None):
        """
        decrement "retries_left"
        if "retries_left" == 0
            delete retry object from db
            update message
                status = "FAILED"
                note_ = <error_message>
        else
            scheduled = now() + delta
        """

        retry = await TelegramMessageRetry.get_retry(message_id=self.id)
        # retry does not exist on this point (retry.retries_left <= 0)

        if retry is None or retry.retries_left <= 0:
            status = await models.LookupMessageSendingStatus.get(
                code='FAILED'
            )
            message = self.update_from_dict(
                {
                    'status': status,
                    'note': note if isinstance(note, str) else ''
                }
            )
            await message.save()
        else:
            await retry.decrement()
            retry.scheduled_on = timezone.now() + datetime.timedelta(seconds=600)
            await retry.save()
        return self


class TelegramMessageRetry(Model):
    class Meta:
        table = 'telegram_messages_retry'

    id = fields.UUIDField(pk=True)
    message = fields.ForeignKeyField('telegram.TelegramMessage', null=False, unique=True)
    scheduled_on = fields.DatetimeField(auto_now=True, index=True)
    retries_left = fields.SmallIntField(default=5)

    @classmethod
    async def get_all_retries(cls):
        return await cls.all()

    @classmethod
    async def create_retry(cls, message: TelegramMessage):
        retry = await cls.create(message=message)
        await retry.save()

    @classmethod
    async def get_retry(
            cls,
            retry_id: Union[uuid.UUID, str] = None,
            message_id: Union[uuid.UUID, str] = None,
    ):
        if retry_id is not None:
            retry = await cls.filter(id=retry_id).get_or_none()
        elif message_id is not None:
            retry = await cls.filter(message__id=message_id).get_or_none()
        else:
            raise Exception('Retry not found')
        return retry

    async def decrement(self) -> None:
        self.retries_left -= 1

        if self.retries_left > 0:
            await self.save()
        else:
            await self.delete()
