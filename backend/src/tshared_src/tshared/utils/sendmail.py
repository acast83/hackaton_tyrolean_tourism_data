from base3 import http

import aiosmtplib
from os.path import basename


async def smtp_send_mail(sender, sender_name, receiver, receiver_name, subject, message,
                         smtp_relay, smtp_port, username=None, password=None, authenticated=True, attachments=None):
    if authenticated and (not username or not password):
        raise http.HttpNotAcceptable(id_message='MISSING_CREDENTIALS',
                                     message='Username or password for SMTP missing')

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    text = "\n"
    html = message

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    if attachments:
        for item in attachments:
            if type(item)==dict:
                fname = item['filename']
                cid = item['cid']

            elif type(item)==str:
                fname = item
                cid = fname

            else:
                raise http.HttpInternalServerError(id_message='INVALID_ATTACHMENT')

            try:
                with open(fname, 'rb') as f:
                    ext = fname.split('.')[-1:]
                    attachedfile = MIMEApplication(f.read(), _subtype=ext)

                    attachedfile.add_header('content-id', f'<{cid}>')
                    attachedfile.add_header('content-disposition', 'attachment', filename=basename(fname))
                    msg.attach(attachedfile)
            except Exception as e:
                raise http.HttpInternalServerError(id_message='CANT_OPEN_FILE_FOR_ATTACHMENT', message=fname)

    try:
        print("SENDING MAIL ", smtp_relay, smtp_port, 'AUTHENTICATED', authenticated)
        smtpObj = aiosmtplib.SMTP()
        await smtpObj.connect(hostname=smtp_relay, port=smtp_port)
        if authenticated:
            await smtpObj.login(username, password)
        await smtpObj.sendmail(sender, receiver, msg.as_string())
        await smtpObj.quit()
    except Exception as e:
        return False, {'code': e.code, 'message': e.message}

    return True, None
