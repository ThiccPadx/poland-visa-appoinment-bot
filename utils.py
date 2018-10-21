
import time
import string
import random
from random import uniform
import logging
import os

__filename__ = 'utils'
logger = logging.getLogger(__filename__)


# input: 2 floats
# output: random float between a and b
def wait_between(a, b):
    time.sleep(uniform(a, b))

# input: string
# output: if string has numbers or not


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


# return random email
def randomEmail():
    domains = ["hotmail.com", "gmail.com", "aol.com",
               "mail.com", "mail.kz", "yahoo.com"]
    letters = string.ascii_lowercase[:12]
    length = random.randint(5, 10)
    d = random.choice(domains)
    n = ''.join(random.choice(letters) for i in range(length))
    e = [n + '@' + d for i in range(1)]

    e = ''.join(e)  # to string

    return str(e)
    pass

# return random password


def randomPass(length=8):
    chars = string.ascii_letters + string.digits
    random.seed = (os.urandom(1024))
    s = ''.join(random.choice(chars) for i in range(length))

    return str(s)
    pass


def getruCaptchaKey():
    return "aaaaaa13d9a6e15177e956169e6e565f"
    pass


def addSuccessToCaptchaHis(logsPath):
    try:
        # insert sucess into captcha history
        f = open(logsPath + '/historyCaptcha.txt', 'a+b')
        f.write('\nCaptcha success')
        f.close()
    except(IOError, Exception) as e:
        print (
            'Failed to save captcha status to history captcha records. File not found.')
        logging.error(
            'Cannot write captcha status to history captcha records. Reason {0}'.format(str(e)))
        pass


def addFailureToCaptchaHis(logsPath):
    try:
        f = open(logsPath + '/historyCaptcha.txt', 'a+b')
        f.write('\nCaptcha failed')
        f.close()
    except (IOError, Exception) as e:
        print (
            'Failed to save captcha status to history captcha records. File not found.')
        logging.error(
            'Cannot write captcha status to history captcha records. Reason {0}'.format(str(e)))
        pass


def addCaptchaSolvingStats(logsPath, stringToTick, c):
    try:
        # insert into captcha history
        f = open(logsPath + '/historyCaptcha.txt', 'a')
        f.write('\nreceived captcha answer {0} in {1} seconds \n'.format(
            str(stringToTick), c * 3))
        f.close()
    except (IOError, Exception) as e:
        print (
            'Failed to save captcha status to history captcha records. File not found.')
        logging.error(
            'Cannot write captcha status to history captcha records. Reason {0}'.format(str(e)))
        pass
    pass
