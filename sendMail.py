# -*- coding: utf-8 -*-
# send email to the operator if recepient number is not valid (step 8)

import smtplib
import logging
import time

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


__filename__ = 'email'

logger = logging.getLogger(__filename__)


def sendRecepientError(applicationID):
    m = u'Receipt Number not accepted by visa center site. Application is Paused.\n Please double-check if it was entered correctly and change status to Active once you clarify the issue.”\n (“Номер квитанції не вдалося знайти при реєстрації на сайті візового центру.\n Заявка призупинена. Будь ласка, переконайтеся, що номер квитанції введено правильно і змініть статус заявки на “Активна” після того, як введете правильні дані.'.encode(
        'utf-8')
    m += '\n'
    m += str(applicationID)
    m += str(time.strftime("%c"))
    ttl = 'Recepient Number {0} Registration Error.'.format(
        str(applicationID))
    send(m, ttl)
    pass


def sendNoDateAvailable(applicationID):

    m = u'No dates available for applicant {0}'.format(str(applicationID))
    m += '\n Date: {0}'.format(str(time.strftime("%c")))
    ttl = 'No dates available for applicant {0}'.format(str(applicationID))
    send(m, ttl)
    pass


def sendFailure(applicationID, reason):
    m = 'Failed to register applicant {0}'.format(str(applicationID))
    m += '\n Reason: {0}'.format(str(reason))
    m += '\n Date: {0}'.format(str(time.strftime("%c")))
    ttl = 'Error Registering applicant {0}'.format(str(applicationID))
    send(m, ttl)
    pass


def send(message, title):
    try:
        # connecting to the email the mail will be sent from (gmail)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login("example@gmail.com", "example")

        receiver = 'example@gmail.com'
        sender = 'example@gmail.com'

        # Create message container - the correct MIME type is
        # multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = title
        msg['From'] = sender
        msg['To'] = receiver

        # Record the MIME types of both parts - text/plain and text/html.

        txt = str(message)
        # Record the MIME types of both parts - text/plain and text/html.

        body = MIMEText(txt, 'plain')

        msg.attach(body)

        server.sendmail(sender,
                        receiver, msg.as_string())
        logging.info(
            'Succeeded sending email with to {0}'.format(str(receiver)))
        server.quit()
        print ('sent email!')
    except smtplib.SMTPException as e:
        logging.info(
            'Failed to send email with message {0} to the operator. Reason: {1}'.format(str(message, e)))
        print 'Error sending mail!'
        server.quit()
