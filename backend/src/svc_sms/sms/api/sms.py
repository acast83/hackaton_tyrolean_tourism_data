import uuid, json
import copy
import base3.handlers
from base3 import http
import tortoise.timezone
from base3.core import Base
from base3.decorators import route, api
from tortoise.transactions import in_transaction
from .. import models
from tshared.utils.sms import send_sms
from . import config
import datetime
import logging

db_connection = 'conn_sms'

from tshared.ipc.tenants import check_user_by_x_api_key


@route('/about')
class SMSAboutHandler(Base):
    @api(auth=False)
    async def get(self):
        """
        Get about information.

        Responses:
            @sms/GET_200_documentation_get_about.json
        """
        return {'service': 'sms'}


@route('/options')
class SMSOptionsHandler(base3.handlers.BaseOptionsHandler):
    model_Option = models.Option
    db_connection = db_connection


@route('/enqueue')
class HandlerSMSEnqueue(base3.handlers.Base):

    @api(weak=True, weak_restricted_on_local=True)
    async def post(self):
        """
        Post enqueue SMS message. TODO

        Parameters: TODO

        RequestBody:
            @sms/POST_201_documentation_post_enqueue_sms.request_body.json

        Responses:
            @sms/POST_201_documentation_post_enqueue_sms.json
        """
        async with in_transaction(connection_name=db_connection):
            sms = await models.SMSQueue.base_create(handler=self, skip_uid=True)
            if not sms:
                raise http.HttpInternalServerError(id_message='ERROR_ENQUEUING_SMS')

            await sms.save()

            return {'id': sms.id}, http.status.CREATED


@route('/tests/last-enqueued')
class TestOnlyHandlerLastEnqueuedSMS(base3.handlers.Base):

    @api(test_only=True)
    async def get(self):
        """
        Get last enqueued SMS.

        Responses:
            @sms/GET_200_documentation_get_last_enqueued.json
        """
        for sms in await models.SMSQueue.all().order_by('-created').limit(1):
            break
        if not sms:
            raise http.HttpErrorNotFound

        return await sms.serialize()


async def do_send_sms(handler, body):
    async with in_transaction(connection_name=db_connection):
        if 'message' in body:
            default_profile = config['default_profile']
            profile = config['profiles'][default_profile]
            sender_number = profile['default_sender']
            body['message'] = body['message'].replace('{{sender_phone_number}}', str(sender_number))

        sms = await models.SMSQueue.base_create(handler=handler, skip_uid=True, body=body)
        if not sms:
            raise http.HttpInternalServerError(id_message='ERROR_ENQUEUING_SMS')

        await sms.save()

        from base3.test import test_mode

        if test_mode:
            sms.sent_to_gateway = tortoise.timezone.now()
            sms.status = {
                'status': 'test-mode-mocked', 'code': 0, 'message': 'sending sms is mocked in tests'}
            await sms.save()
            res = copy.deepcopy(sms.status)
            res['id'] = uuid.uuid4()
            res['sender'] = sender_number
            res['receiver'] = sms.target_number
            res['message'] = sms.message
            return res

        success, message = await send_sms(handler.request, config, sms.target_number, sms.message)

        sms.sent_to_gateway = tortoise.timezone.now()

        if success:
            sms.status = {'status': 'sent-to-gateway'}
            if message:
                try:
                    msg = json.loads(message)
                    sms.status.update(msg)
                    sms.price = msg['list'][0]['points']
                    sms.external_id = msg['list'][0]['id']
                except:
                    sms.status.update(message)

        else:
            sms.status = {'status': 'error-sending-to-gateway'}
            sms.status.update(message)

        await sms.save()

        return {'id': sms.id,
                'receiver': sms.target_number,
                'sender': sender_number,
                'message': sms.message}


@route('/send-x/:x_api_key')
class HandlerSMSXAPIKEY(base3.handlers.Base):

    @api(weak=True)
    async def post(self, x_api_key:uuid.UUID):
        await check_user_by_x_api_key(handler=self, x_api_key=x_api_key, config=config)

        body = self.request_body()
        return await do_send_sms(self, body)


@route('/send')
class HandlerSMSX(base3.handlers.Base):

    @api(weak=True, weak_restricted_on_local=True)
    async def post(self):
        """
        Post send SMS. TODO

        Parameters: TODO

        RequestBody:
            @sms/POST_200_documentation_post_send_sms.request_body.json

        Responses:
            @sms/POST_200_documentation_post_send_sms.json
        """

        body = self.request_body()
        return await do_send_sms(self, body)

        # if True:
        # async with in_transaction(connection_name=db_connection):
        #     if 'message' in body:
        #         default_profile = config['default_profile']
        #         profile = config['profiles'][default_profile]
        #         sender_number = profile['default_sender']
        #         body['message'] = body['message'].replace('{{sender_phone_number}}', str(sender_number))
        #
        #     sms = await models.SMSQueue.base_create(handler=self, skip_uid=True, body=body)
        #     if not sms:
        #         raise http.HttpInternalServerError(id_message='ERROR_ENQUEUING_SMS')
        #
        #     await sms.save()
        #
        #     from base3.test import test_mode
        #
        #     if test_mode:
        #         sms.sent_to_gateway = tortoise.timezone.now()
        #         sms.status = {
        #             'status': 'test-mode-mocked', 'code': 0, 'message': 'sending sms is mocked in tests'}
        #         await sms.save()
        #         res = copy.deepcopy(sms.status)
        #         res['id'] = uuid.uuid4()
        #         res['sender'] = sender_number
        #         res['receiver'] = sms.target_number
        #         res['message'] = sms.message
        #         return res
        #
        #     success, message = await send_sms(self.request, config, sms.target_number, sms.message)
        #
        #     sms.sent_to_gateway = tortoise.timezone.now()
        #
        #     if success:
        #         sms.status = {'status': 'sent-to-gateway'}
        #         if message:
        #             try:
        #                 msg = json.loads(message)
        #                 sms.status.update(msg)
        #                 sms.price = msg['list'][0]['points']
        #                 sms.external_id = msg['list'][0]['id']
        #             except:
        #                 sms.status.update(message)
        #
        #     else:
        #         sms.status = {'status': 'error-sending-to-gateway'}
        #         sms.status.update(message)
        #
        #     await sms.save()
        #
        #     return {'id': sms.id,
        #             'receiver': sms.target_number,
        #             'sender': sender_number,
        #             'message': sms.message}
        #

@route('/:id_sms/send')
class HandlerSendEnqueuedSMS(base3.handlers.Base):
    """
        Parameters:
            id_sms (path): Id of SMS
    """

    @api(weak=True, weak_restricted_on_local=True)
    async def post(self, id_sms: uuid.UUID):
        """
        Post send single SMS. TODO

        Parameters: TODO


        RequestBody:
            @sms/POST_200_documentation_post_send_single_sms.request_body.json

        Responses:
            @sms/POST_200_documentation_post_send_single_sms.json
        """

        sms = await models.SMSQueue.base_fetch_single(id=id_sms, id_tenant=self.id_tenant, return_orm_object=True)

        from base3.test import test_mode

        if test_mode:
            sms.sent_to_gateway = tortoise.timezone.now()
            sms.status = {'status': 'test-mode-mocked', 'code': 0, 'message': 'sending sms is mocked in tests'}
            await sms.save()
            res = copy.deepcopy(sms.status)
            res['id'] = uuid.uuid4()
            return res

        try:
            suceess, message = await \
                send_sms(self.request, config, sms.target_number, sms.message)
        except Exception as e:
            raise

        success, message = await send_sms(self.request, config, sms.target_number, sms.message)

        sms.sent_to_gateway = tortoise.timezone.now()

        if success:
            sms.status = {'status': 'sent-to-gateway'}
        else:
            sms.status = {'status': 'error-sending-to-gateway'}
            sms.status.update(message)

        await sms.save()

        return {'success_status': suceess, 'err_message': message}


@route('/delivery_report/:x_api_key')
class HandlerSMSDeliveryReport(base3.handlers.Base):

    # OVAJ GET TREBA DA ZOVE POST ZBOG BALANSINGA JER GET JE READ ONLY ALI SMSAPI TRAZI GET

    @api(weak=True, raw=True)
    async def get(self, x_api_key):  # external_id: str):

        await check_user_by_x_api_key(handler=self, x_api_key=x_api_key, config=config)

        external_id = self.get_argument('MsgId', None)

        sms = await models.SMSQueue.filter(external_id=external_id).get_or_none()

        if sms:
            if not sms.delivery_report_response:
                sms.delivery_report_response = []

            j = json.loads(json.dumps(self.request.arguments, default=lambda x: str(x), ensure_ascii=False))
            sms.delivery_report_response.append({'timestamp': str(tortoise.timezone.now()), 'data': j})

            if 'status_name' in j and 'DELIVERED' in str(j['status_name']) and sms.delivery_confirmed_timestamp is None:
                sms.delivery_confirmed_timestamp = tortoise.timezone.now()

            await sms.save()

        self.write('OK')
        return None


@route('/poll/:x_api_key')
class SMSPollHandler(Base):

    @api(weak=True)
    async def post(self, x_api_key: uuid.UUID, limit: int = 10, from_number: str = None):

        await check_user_by_x_api_key(handler=self, x_api_key=x_api_key, config=config)

        filters = {'id_tenant': self.id_tenant, 'polled__isnull': True, 'active': True}
        if from_number:
            filters['from_number'] = from_number

        messages = await models.ReceivedSMS.filter(**filters).order_by('created').limit(limit).all()

        res = []
        async with in_transaction(connection_name=db_connection):
            for m in messages:
                res.append(await m.serialize(fields=['id', 'created', 'from_number', 'to_number', 'message']))  # 'id,created,from_numbber,to_number,message'))
                m.polled = tortoise.timezone.now()
                await m.save()

        return res


@route('/receive/:x_api_key')
class SMSReceiveHandler(Base):

    @api(weak=True, raw=True)
    async def post(self, x_api_key: uuid.UUID):

        try:
            await check_user_by_x_api_key(handler=self, x_api_key=x_api_key, config=config)
        except Exception as e:
            print("EEEE", e)
            raise

        sms_from = self.get_argument('sms_from', None)
        _sms_to = self.get_argument('sms_to', None)
        _sms_time = self.get_argument('sms_date', None)
        _sms_date = None
        if _sms_time:
            _sms_date = str(datetime.datetime.fromtimestamp(int(_sms_time)))
        _sms_text = self.get_argument('sms_text', None)
        _username = self.get_argument('username', None)
        _received = str(datetime.datetime.now())

        if sms_from:
            sms_from = sms_from.strip()
            if len(sms_from) and sms_from[0] != '+':
                sms_from = f'+{sms_from}'

        x = [sms_from, _sms_to, _sms_time, _sms_date, _sms_time, _sms_text, _username, _received]

        log = logging.getLogger('olo_sms')
        log.info(f"SMS RECEIVED {x}")

        rsms = models.ReceivedSMS(
            id_tenant=self.id_tenant,
            created_by=self.id_user, last_updated_by=self.id_user,
            from_number=sms_from,
            to_number=_sms_to,
            message=_sms_text,
        )
        await rsms.save()

        # await connect_with_operation(self, rsms, log)
        #
        # await rsms.save()

        self.write('OK')
        return None
