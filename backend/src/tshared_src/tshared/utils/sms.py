import json
import datetime
from tornado.httpclient import AsyncHTTPClient
import urllib.parse

async def send_sms(request, config, target, message, scheduled: datetime.datetime = None):

    try:

        default_profile = config['default_profile']

        if default_profile == 'smsapi':
            return await send_sms_via_sms_api(request, config['profiles'][default_profile], target, message, scheduled)

        elif default_profile == 'anysms':
            return await send_sms_via_any_sms(request, config['profiles'][default_profile], target, message, scheduled)

        elif default_profile == 'sms2email':
            from tshared.ipc.sendmail import sendmail
            await sendmail(request, 'digital cube', 'digital@digitalcube.rs', 'digital cube',
                           config['profiles'][default_profile]['endpoint'], f'sms: {message}', f'sms: {message}')

            return True, None

    except Exception as e:
        raise

    return False, 'No default_profile in config'


async def send_sms_via_sms_api(request, profile, target, message, scheduled: datetime.datetime = None):
    data = {
        'from': profile['default_sender'],
        'to': target,
        'message': message,
        'format': 'json'
    }


    _params = urllib.parse.urlencode(data)
    _headers = {'Authorization': f'Bearer {profile["api_key"]}'}
    _url = f'{profile["endpoint"]}?{_params}'

    http_client = AsyncHTTPClient()
    try:
        result = await http_client.fetch(_url, headers=_headers, request_timeout=100)
    except Exception as e:
        raise
        
    if result.code in (200, 201, 204):
        return True, result.body

    return False, 'Error smsapi'


async def send_sms_via_any_sms(request, profile, target, message, scheduled: datetime.datetime = None):
    def schedule_formatter(scheduled: datetime.datetime):
        '''
                variable for delayed delivery. Format is explained below:
                Y = year 4 digit length, M = month 2 digit length, D = day 2 digit
                length, H = hour 2 digit length, I = minute 2 digit length
                2016-09-20 13:00:00
        '''
        scheduled = str(scheduled) if scheduled else None
        return scheduled.replace('-', '').replace(' ', '').replace(':', '').replace('T', '') if scheduled else None

    payload = {
        'id': str(profile['uid']),
        'pass': profile['password'],
        'gateway': profile['gateway'],
        'test': 0,
        'xml': 1,
        'notify': 1,
        'long': 1,
        'nummer': target,
        'text': message,
        'absender': 'sms-title',
        'time': schedule_formatter(scheduled),
    }

    try:
        a_http_client = AsyncHTTPClient()

        from tornado.httpclient import HTTPRequest

        try:
            response = await a_http_client.fetch(request=HTTPRequest(url=profile['endpoint'],
                                                                     method='POST',
                                                                     body=json.dumps(payload)))
        except Exception as e:
            print("Error: {e}")
            raise

        print('code', response.code)
        print('body', response.body)

    except Exception as e:
        raise

    return True, None
