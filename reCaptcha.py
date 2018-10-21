# -*- coding: utf-8 -*-
# reCaptcha module
import sys
import logging
from utils import *  # add utils
import requests
from threading import Thread
import json
import os
import base64
import urllib

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchFrameException


global timetoslve  # time takes to solve

__file__ = 'reCaptcha.py'

logger = logging.getLogger(__file__)

# ticking google recaptcha checkbox
rootpath = os.path.dirname(os.path.abspath(__file__))
logsPath = rootpath + '/logs'


class Captcha(object):

    # webdriver instance
    def __init__(self, browser):
        self.__browser = browser
        pass
    # checking checkbox

    def selectCheckbox(self):
        wait_between(5, 6)
        try:
            # go to captcha
            s = self.__browser.switch_to_frame(
                self.__browser.find_elements_by_tag_name("iframe")[0])
            # locate CheckBox web element
            CheckBox = WebDriverWait(self.__browser, 10).until(
                EC.presence_of_element_located((By.ID, "recaptcha-anchor")))
            # making click on captcha CheckBox
            CheckBox.click()
            # back to main window
            self.__browser.switch_to_default_content()
            # switch to the second iframe by tag name
            logging.info('Captcha checked')
            print ('captcha checked')
            return True
        except (NoSuchFrameException, TimeoutException, Exception) as e:
            print (str(e) + 'reCaptcha selectCheckbox() function failed')
            logger.info(str(e) + 'reCaptcha selectCheckbox() function failed')
            return False
            pass

    # download captcha image
    def getImage(self):
        wait_between(4, 5)
        try:
            import urllib
            # switch to image iframe
            self.__browser.switch_to_frame(
                self.__browser.find_elements_by_tag_name("iframe")[1])
            img = self.__browser.find_element_by_xpath(
                "//*[@id='rc-imageselect-target']/table/tbody/tr[1]/td[2]/div/div[1]/img")
            src = img.get_attribute('src')
            print (src)
            urllib.urlretrieve(src, 'captcha.jpg')  # save image
            logging.info('Got captcha image on url ' + src)
            return True
        except (NoSuchFrameException, NoSuchElementException, IndexError, Exception) as e:
            print 'Error retreiving reCaptcha image'
            logger.error(
                'Error retreiving reCaptcha image. Reason {0}'.format(str(e)))
            return False

        pass

    # get image challenge instructions
    def getInstructions(self):
        try:
            txt = self.__browser.find_element_by_css_selector(
                '.rc-imageselect-desc-no-canonical').text
        except (NoSuchElementException, Exception) as e:
            print ('Could not get captcha instructions')
            logger.error(
                'Could not get reCaptcha instructions. Reason {0}'.format(str(e)))
            return False
        return txt
        pass

    # get Captchas dimentions - 3*3 or 4*4 or 4*2
    def getCaptchaDimention(self):
        d = int(self.__browser.find_element_by_xpath(
            '//div[@id="rc-imageselect-target"]/table').get_attribute("class")[-1])
        return d if d else 3  # dimention is 3 by default

    # solving captcha
    def Solve(self):

        # get recaptcha challenge image
        # Enters loop on bad captcha
        if self.getImage() == False:
            # switch to first iframe
            print ('Error with getting captcha image')
            logging.error('Error with getting captcha image')
            self.__browser.switch_to_frame(
                self.__browser.switch_to_default_content())
            # refresh page and start captcha solving again
            return False
            pass

        instructions = self.getInstructions()

        # if instructions is false
        if len(instructions) < 10:
            print 'Error at captcha img/instructions fetching'
            logging.error('Error at captcha img/instructions fetching')
            return False

        # try ruCaptcha
        print 'Asking Rucaptcha for answer'
        # ready to receive answer (what images to tick)
        ans = self.ruCaptcha(instructions)
        if ans != '':
            if(self.tickImages(ans)) == False:
                return False
                pass
            else:
                # when image are ticked
                return True
        return False

    # response answer
    # sending captcha to rucaptcha service
    def ruCaptcha(self, instructions):
        url = 'http://rucaptcha.com/in.php'
        files = {'file': open("captcha.jpg", "rb")}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}

        data = {'key': getruCaptchaKey(), 'method': 'post'}
        data = {
            'method': 'post',
            'key': getruCaptchaKey(),
            'textinstructions': instructions,
        }

        # post with image and instructions
        response = requests.post(url, files=files, data=data)
        print response.content
        cID = str(response.content)
        cID = cID[3:]
        print cID

        resp_url = 'http://rucaptcha.com/res.php?key=aaaaaa13d9a6e15177e956169e6e565f&action=get&json=1&id=' + cID

        print resp_url
        global c
        c = 0

        while True:
            try:
                response = requests.get(resp_url, headers=headers)
                print response.content
                data = json.loads(response.content)
                captcha_token = data['request']
                status = data['status']
            except (ValueError, Exception) as e:
                print (e)
                return ''
            if captcha_token == 'CAPCHA_NOT_READY' and status == 0 and c < 60:
                print 'sleep'
                wait_between(3.0, 3.1)
                c = c + 1

            elif captcha_token == 'ERROR_CAPTCHA_UNSOLVABLE' and status == 0 and c < 60:
                print 'captcha failed, trying again.'
                logging.info('Captcha failed, trying again.')
                wait_between(3.0, 3.1)
                c = c + 1
                return ''

            elif captcha_token == 'ERROR_IMAGE_TYPE_NOT_SUPPORTED':
                print 'captcha image type is not supported'
                logging.info('captcha image type is not supported')

                return ''
            elif captcha_token == 'ERROR_WRONG_CAPTCHA_ID':
                print 'Error captcha ID'
                logging.error('Error captcha id')
                return ''

            elif captcha_token == 'ERROR_KEY_DOES_NOT_EXIST':
                print 'Error with rucaptcha key'
                logging.error('Error with rucaptcha key')
                return ''
                pass
            elif captcha_token == 'ERROR_WRONG_ID_FORMAT':
                print 'Error with ID format'
                logging.error('Error with ID format')
                return ''

                pass
            elif captcha_token == 'ERROR_BAD_DUPLICATES':
                print 'Error bad duplicates'
                logging.error('Error bad duplicates')
                return ''
                pass

            elif captcha_token == 'REPORT_NOT_RECORDED':
                print 'Report was not recorded'
                logging.error('Report was not recorded')
                return ''
                pass

            elif hasNumbers(str(captcha_token.decode('utf-8'))) and status == 1:  # captcha answer
                print 'found numbers!'
                logging.info('found captcha {0}'.format(str(captcha_token)))
                return str(captcha_token)

                break
            else:
                return False
                pass
            pass

        pass

    # input : list of correct answers
    # output: ticking theses imagaes
    def tickImages(self, stringToTick):
        global c
        print 'Found Answer! {0}'.format(str(stringToTick))
        l = []

        try:
            for i in stringToTick:
                print i
                l.append(int(i))
        except (ValueError, TypeError, Exception) as e:
            print 'error with captcha answer response'
            return False

        try:
            dim = self.getCaptchaDimention()  # get captcha dimentions
            logging.info('captcha size is {0}'.format(int(dim)))
            print 'Dimention is: ', dim

            wait_between(2, 3)

            if int(dim) == 2:  # 4*2
                for i in l:
                    if i < 3:
                        # append first row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(1, i)).click()
                        pass
                    elif i > 2 and i < 5:
                        # append second row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(2, i - 2)).click()
                        pass
                    elif i > 4 and i < 7:
                        # appden third row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(3, i - 4)).click()
                        pass
                    elif i > 6 and i < 9:
                        # append fourth row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(4, i - 6)).click()
                    else:
                        print 'error clicking a tile'
                        logging.error(
                            'Failed to mark captcha image challange')
                pass

            elif int(dim) == 3:  # 3*3
                for i in l:
                    if i < 4:
                        # append first row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(1, i)).click()
                        pass
                    elif i < 7 and i > 3:
                        # append second row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(2, i - 3)).click()
                        pass
                    elif i > 6 and i < 10:
                        # append third row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(3, i - 6)).click()
                        pass
                    else:
                        print 'error clicking a tile'
                        logging.error(
                            'Failed to mark captcha image challange')

                pass

            elif int(dim) == 4:  # 4*4
                for i in l:
                    if i < 5:
                        # append first row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(1, i)).click()
                        pass
                    elif i > 4 and i < 9:
                        # append second row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(2, i - 4)).click()
                        pass
                    elif i > 8 and i < 13:
                        # append third row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(3, i - 8)).click()
                        pass
                    elif i > 12 and i < 17:
                        # append fourth row
                        self.__browser.find_element_by_xpath(
                            '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(3, i - 12)).click()
                        pass
                    else:
                        print 'error clicking a tile'
                        logging.error(
                            'Failed to mark captcha image challange')
                pass
            else:
                print 'Error in image dimentions'
                logging.error('Error is image dimentions')

            # add to captcha history
            addCaptchaSolvingStats(logsPath, stringToTick, c)

            # logging
            logging.info('received captcha answer {0}'.format(
                str(stringToTick)))
            logging.info('time took to solve {0} seconds'.format(c * 3))
            return True
        except Exception as e:
            logging.info(str(e))
            print (e)
            return False
        pass
    pass


class ruAccount(object):

    def __init__(self, key):
        self.__key = key
        pass

    @classmethod
    def getBalance(self, key):
        r = requests.get('http://rucaptcha.com/res.php?key=' +
                         key + '&action=getbalance')
        return str(r.content)

    @staticmethod  # 2013-11-28
    def getStats(self, year=0, data=0, month=0):
        r = requests.get('http://rucaptcha.com/res.php?key=')
        return str(r.content)

    pass
