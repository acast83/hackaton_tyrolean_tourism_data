import os
import json
import uuid
import copy
import base3.handlers
import tortoise.timezone
from . import config
from .. import models
from base3 import http
from base3.core import Base
import tshared.ipc.files as ipc_files
from base3.decorators import route, api
from tornado.httpclient import AsyncHTTPClient
from tortoise.transactions import in_transaction
from tshared.utils.sendmail import smtp_send_mail

db_connection = 'conn_sendmail'


@route('/about')
class SendmailAboutHandler(Base):
    """
    Get about information

    Responses:
        @sendmail/GET_200_documentation_get_about.json
    """

    @api(auth=False)
    async def get(self):
        return {'service': 'sendmail'}


@route('/options')
class SendmailOptionsHandler(base3.handlers.BaseOptionsHandler):
    model_Option = models.Option
    db_connection = db_connection


def get_default_sender_info():
    try:
        profile = config['default_profile']
    except Exception as e:
        profile = 'sendinblue_smtp'

    c = config['profiles'][profile]

    if 'default_mail_sender' in c:
        if 'display_name' not in c['default_mail_sender']:
            raise http.HttpInternalServerError(id_message='CONFIGURATION_ERROR_MISSING_DEFAULT_MAIL_SENDER_DISPLAY_NAME_IN_ACTIVE_SENDMAIL_PROFILE')
        if 'email' not in c['default_mail_sender']:
            raise http.HttpInternalServerError(id_message='CONFIGURATION_ERROR_MISSING_DEFAULT_MAIL_SENDER_EMAIL_IN_ACTIVE_SENDMAIL_PROFILE')
        dfs_display_name = c['default_mail_sender']['display_name']
        dfs_email = c['default_mail_sender']['email']

    elif 'default_mail_sender' in config:
        if 'display_name' not in config['default_mail_sender']:
            raise http.HttpInternalServerError(id_message='CONFIGURATION_ERROR_MISSING_DEFAULT_MAIL_SENDER_DISPLAY_NAME_IN_SENDMAIL_SERVICE_CONFIG')
        if 'email' not in config['default_mail_sender']:
            raise http.HttpInternalServerError(id_message='CONFIGURATION_ERROR_MISSING_DEFAULT_MAIL_SENDER_EMAIL_IN_ACTIVE_SENDMAIL_SERVICE_CONFIG')

        dfs_display_name = config['default_mail_sender']['display_name']
        dfs_email = config['default_mail_sender']['email']

    else:
        from . import app_config
        if 'default_mail_sender' not in app_config['application']:
            raise http.HttpInternalServerError(id_message='CONFIGURATION_ERROR_MISSING_DEFAULT_MAIL_SENDER_DISPLAY_NAME_IN_APP_CONFIG')
        if 'email' not in config['default_mail_sender']:
            raise http.HttpInternalServerError(id_message='CONFIGURATION_ERROR_MISSING_DEFAULT_MAIL_SENDER_EMAIL_IN_APP_CONFIG')

        dfs_display_name = app_config['application']['default_mail_sender']['display_name']
        dfs_email = app_config['application']['default_mail_sender']['email']

    dfs_display_name = dfs_display_name.strip() if dfs_display_name else None
    dfs_email = dfs_email.strip() if dfs_email else None

    if not dfs_email and not dfs_display_name:
        raise http.HttpInternalServerError(id_message='CONFIGURATION_ERROR_MISSING_DEFAULT_MAIL_SENDER_INFO_CONFIGURATION')

    return dfs_email, dfs_display_name


@route('/enqueue')
class HandlerSendmailEnqueue(base3.handlers.Base):

    @api(weak=True, weak_restricted_on_local=True)
    async def post(self):
        """
        Enqueue mail TODO requestbody

        Parameters:

        RequestBody:
            @sendmail/POST_201_documentation_post_enqueue_mail.request_body.json

        Responses:
            @sendmail/POST_201_documentation_post_enqueue_mail.json
        """

        import tshared.utils.send_telegram_message as telegram
        a = telegram.publish_message(message_text='sendmail: {}'.format(json.dumps(json.loads(self.request.body), indent=1)))

        async with in_transaction(connection_name=db_connection):
        # if True:
            body = self.request_body()

            if 'sender_email' not in body or 'sender_display_name' not in body:
                dfs_email, dfs_display_name = get_default_sender_info()
                if 'sender_email' not in body:
                    body['sender_email'] = dfs_email
                if 'sender_display_name' not in body:
                    body['sender_display_name'] = dfs_display_name

            email = await models.MailQueue.base_create(handler=self, skip_uid=True, body=body)
            if not email:
                raise http.HttpInternalServerError(id_message='ERROR_ENQUEUING_EMAIL')

            await email.save()

            return {'id': email.id}, http.status.CREATED


@route('/tests/last-enqueued')
class TestOnlyHandlerLastEnqueuedEmail(base3.handlers.Base):

    @api(test_only=True)
    async def get(self):
        """
        Get last enqueued mail

        Responses:
            @sendmail/GET_200_documentation_get_last_enqueued_mail.json
        """

        for email in await models.MailQueue.all().order_by('-created').limit(1):
            break
        if not email:
            raise http.HttpErrorNotFound

        return await email.serialize()


# todo: remove this!!!!
@route('/tests-last-few')
class LastFewHandlerLastEnqueuedEmail(base3.handlers.Base):

    @api(auth=False)
    async def get(self):
        """
        Get last few e-mails

        Responses:
            @sendmail/GET_200_documentation_get_last_enqueued_mail1.json
        """

        emails = await models.MailQueue.all().order_by('-created').limit(10)
        res = [await email.serialize(fields=('created', 'receiver_email', 'subject', 'html_body')) for email in emails]

        for x in res:
            x['pin'] = x['subject'].split('PIN:')[-1].strip() if 'PIN:' in x['subject'] else 'N/A'
            if 'reset password code is' in x['html_body']:
                x['reset_password_code'] = x['html_body'].split('reset password code is:')[-1].strip()[:36]

        return {'mails': res}


@route('/send-attached-document')
class HandlerSendDocument(base3.handlers.Base):

    @api()
    async def post(self, files, emails):

        if type(files) == str:
            files = files.replace(';', '').split(',')

        if type(emails) == str:
            emails = emails.replace(' ', '').replace(';', ',').split(',')

        token = self.request.headers['Authorization'].split(' ')[-1]

        attachments = []
        http_client = AsyncHTTPClient()
        for f in files:
            url = f'http://v3/api/v3/files/static/{f}?token={token}'
            response = await http_client.fetch(url)

            with open(f'/tmp/{f}', 'wb') as file:
                file.write(response.body)
            #            cmd = f'/usr/bin/curl \"http://v3/api/v3/files/static/{f}?token={token}\" --output /tmp/{f}'
            #            self.log.critical(cmd)
            #            os.system(cmd)

            attachments.append(f'/tmp/{f}')

        c = config['profiles']['sendinblue_smtp']
        c = config['profiles']['sendgrid_telmekom_smtp']

        for email in emails:

            dfs_email, dfs_display_name = get_default_sender_info()

            b = {
                'id_tenant': self.id_tenant,
                'created_by': self.id_user,
                'last_updated_by': self.id_user,
                'sender_email': dfs_email,
                'sender_display_name': dfs_display_name,
                'receiver_email': email,
                'receiver_display_name': email,
                'subject': 'Attachment',
                'body': 'Files are attached in this email',
                'html_body': '<p>Files are attached in this email</p>',
                'attachments': attachments
            }
            db_email = await models.MailQueue.base_create(handler=self, skip_uid=True, body=b)
            await db_email.save()

            success, message = await \
                smtp_send_mail(db_email.sender_email, db_email.sender_display_name,

                               #                            [{'name':db_email.receiver_email,'email':db_email.receiver_display_name}],
                               db_email.receiver_email,
                               None,

                               db_email.subject, db_email.html_body,
                               c['smtp_relay'], c['smtp_port'], username=c['username'],

                               password=c['password'], authenticated=c['authenticated'], attachments=attachments

                               )

        return {'sent': True}


@route('/send')
class HandlerSendmail(base3.handlers.Base):

    @api(weak=True, weak_restricted_on_local=True)
    async def post(self):
        """
        Post send mail TODO requestbody

        Parameters:

        RequestBody:
            @sendmail/POST_200_documentation_post_send_mail.request_body.json

        Responses:
            @sendmail/POST_200_documentation_post_send_mail.json
        """
        from base3.test import test_mode  # TODO why does it need to be exactly here and not on top of the file?
        async with in_transaction(connection_name=db_connection):
        # if True:

            body = self.request_body()

            if 'sender_email' not in body or 'sender_display_name' not in body:
                dfs_email, dfs_display_name = get_default_sender_info()
                if 'sender_email' not in body:
                    body['sender_email'] = dfs_email
                if 'sender_display_name' not in body:
                    body['sender_display_name'] = dfs_display_name

            email = await models.MailQueue.base_create(handler=self, skip_uid=True, body=body)

            if not email:
                raise http.HttpInternalServerError(id_message='ERROR_ENQUEUING_EMAIL')

            await email.save()

            if test_mode:
                email.sent_to_gateway = tortoise.timezone.now()
                email.status = {'status': 'test-mode-mocked', 'code': 0, 'message': 'sending mail is mocked in tests'}
                await email.save()
                res = copy.deepcopy(email.status)
                res['id'] = uuid.uuid4()
                return res

            c = config['profiles']['sendinblue_smtp']

            attachments = None
            if 'attachments' in self.request_body():
                attachments = self.request_body()['attachments']

            success, message = await \
                smtp_send_mail(email.sender_email, email.sender_display_name,
                               email.receiver_email, email.receiver_display_name,
                               email.subject, email.html_body,
                               c['smtp_relay'], c['smtp_port'], username=c['username'],
                               password=c['password'], authenticated=c['authenticated'], attachments=attachments, )

            if success:
                email.status = {'status': 'sent-to-gateway'}
            else:
                email.status = {'status': 'error-sending-to-gateway'}
                email.status.update(message)

            email.sent_to_gateway = tortoise.timezone.now()
            await email.save()

            return email.status


@route('/:id_item/send')
class HandlerSendEnqueuedEmail(base3.handlers.Base):
    """
    Parameters:
        id_item (path): Item ID
    """

    @api(weak=True, weak_restricted_on_local=True)
    async def post(self, id_email: uuid.UUID):
        """
        Post send specific email TODO requestbody

        Parameters:
            id_email (body): Email ID

        RequestBody:
            @sendmail/POST_200_documentation_post_send_specific_mail.request_body.json

        Responses:
            @sendmail/POST_200_documentation_post_send_specific_mail.json
        """
        email = await models.MailQueue.base_fetch_single(id=id_email, id_tenant=self.id_tenant, return_orm_object=True)

        if not email or email.sent_to_gateway:
            raise http.HttpErrorNotFound

        from base3.test import test_mode

        if test_mode:

            if 'no_test' in self.request_body() and self.request_body()['no_test']:
                pass
            else:
                email.sent_to_gateway = tortoise.timezone.now()
                email.status = {'status': 'test-mode-mocked', 'code': 0, 'message': 'sending mail is mocked in tests'}
                await email.save()
                res = copy.deepcopy(email.status)
                res['id'] = uuid.uuid4()
                return res

        try:
            profile = config['default_profile']
        except Exception as e:
            profile = 'sendinblue_smtp'

        c = config['profiles'][profile]

        success, message = await \
            smtp_send_mail(email.sender_email, email.sender_display_name,
                           email.receiver_email, email.receiver_display_name,
                           email.subject, email.html_body,
                           c['smtp_relay'], c['smtp_port'], username=c['username'],
                           password=c['password'], authenticated=c['authenticated'],attachments=email.attachments)

        if success:
            email.status = {'status': 'sent-to-gateway'}
        else:
            email.status = {'status': 'error-sending-to-gateway'}
            email.status.update(message)

        email.sent_to_gateway = tortoise.timezone.now()
        await email.save()

        return email.status
