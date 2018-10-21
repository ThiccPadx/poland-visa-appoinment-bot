# -*- coding: utf-8 -*-

""" Registration Poland Visa Centerin Ukraine """

try:
    from selenium import webdriver
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.support.ui import WebDriverWait
    # no element matching exception
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException
    from selenium.common.exceptions import TimeoutException
    from selenium.common.exceptions import NoSuchFrameException
    from selenium.webdriver.common.by import By

    import requests
    import json
    import platform
    import os
    import sys
    import logging
    import threading
    from reCaptcha import *  # recaptcha
    from mssqlPipe import *  # connection pipe to Azure Database
    import sendMail as email
    from utils import *  # all util function

except ImportError as e:
    print e

__author__ = "Gabriel"

__file__ = "register.py"


global projectPath
projectPath = os.path.dirname(os.path.abspath(__file__))

global logsPath
logsPath = projectPath + '/logs'

# creating logging file
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename=logsPath + '/debug.log', filemode='w', level=logging.INFO)


class Register(object):

    __failedToRegister = 0

    def __init__(self):
        self.__ExitImmidiatly = False

        # create error thread

        #    if self.fetchFromTable() == False:
        #        return False

        pass

    def startRegisteringApplicant(self, rn=''):
        self.__rn = rn
        #self.__ppva = ppva
        if self.__rn == '':
            # quit
            return False
        self.register()
        pass

    # perform all registration steps
    def register(self):
        # run 3 times maxmum
        while self.__failedToRegister < 3 or self.__ExitImmidiatly == False:
            self.create_browser()
            self.open_browser()
            self.firstPage()
            wait_between(1, 2)
            self.secondPage()
            wait_between(1, 2)
            self.thirdPage()
            wait_between(1, 2)
            self.submitCaptchaForm()
            wait_between(1, 2)
            self.fourthPage(self.__rn)
            wait_between(1, 2)
            self.fifthPage()
            wait_between(1, 2)
            self.sixthPage()
            pass

        pass

    def handleFailure(self, reason):
        email.sendFailure(self.applicationID, reason)
        return False
        # op

        # delete instance
        pass

    def create_browser(self):
        global projectPath
        try:
            # for mac os x machines / Linux machines
            # binary firefox that Tor is using
            # On Ubuntu machine it is /usr/bin/tor-browser/Browser/firefox
            from sys import platform
            if platform == "linux" or platform == "linux2":
                # linux
                pass
            elif platform == "darwin":
                # OS X
                binary = '/Applications/TorBrowser.app/Contents/MacOS/firefox'
                pass
            elif platform == "win32":
                # Windows...
                pass
            # check if firefox library exists on machine
            if os.path.exists(binary) is False:
                logging.error(
                    'The binary package firefox inside TOR is not found!')
                raise ValueError(
                    'The binary package firefox inside TOR is not found!')
                sys.exit(1)

            firefox_capabilities = DesiredCapabilities.FIREFOX
            # on selenium 3 version Marionette is enabled by default
            firefox_capabilities['marionette'] = True
            firefox_capabilities['binary'] = binary
            import platform
            # check if geckodriver exists
            if os.path.isfile('geckodriver') == False:
                # install geckodriver
                # check if geckodriver is installed on machine
                platformArchitecture = platform.architecture()[0]
                if platformArchitecture == '62bit':
                    # download geckodriver for 63bit
                    pass
                if platformArchitecture == '32bit':
                    # download geckodriver for 32bit
                    pass
                # if not - install

            os.environ[
                "PATH"] += ":/usr/local/lib/python2.7/site-packages/selenium-3.0.1-py2.7.egg/selenium/webdriver/firefox"

            # disablinf all browser add-ons, popups
            profile = webdriver.FirefoxProfile()

            profile.set_preference("pdfjs.disabled", True)

            profile.set_preference("dom.disable_beforeunload", True)

            profile.set_preference('dom.successive_dialog_time_limit', 0)
            profile.set_preference("http.response.timeout", 10)

            # dom.successive_dialog_time_limit 0
            self.__browser = webdriver.Firefox(
                capabilities=firefox_capabilities, firefox_profile=profile)
            print 'created browser'
            wait_between(4, 5)
        except Exception as e:
            print (e)
            logging.error(str(e))
            self.__failedToRegister = self.__failedToRegister + 1
            self.register()

    def open_browser(self):
        # step 1
        try:
            uniqueID = "asdfa"  # random string webserver generates to idenftify client's request
            self.__browser.get("https://polandonline.vfsglobal.com/poland-ukraine-appointment/(S(" + uniqueID +
                               "))/AppScheduling/AppWelcome.aspx?P=s2x6znRcBRv7WQQK7h4MTjZiPRbOsXKqJzddYBh3qCA=")
            wait_between(6, 7)
            print 'opened browser'
        except (Exception, TimeoutException) as e:
            print (e)
            logging.error('Failed to open browser. Reason: {0}'.format(str(e)))
            self.__failedToRegister = self.__failedToRegister + 1
            self.register()

            pass
        logging.debug('Browser opened')
        pass

    def firstPage(self):
        # step 2
        try:
            wait_between(2, 3)
            self.__browser.find_element_by_css_selector(
                '#ctl00_plhMain_lnkSchApp').click()  # Designate the date of filing
            wait_between(3, 4)
        except (NoSuchElementException, Exception) as e:
            print (e)
            logging.error(str(e))
            self.__failedToRegister = self.__failedToRegister + 1
            self.__browser.quit()
            wait_between(3, 4)
            self.register()

    def secondPage(self, ppva=u'Польщі Львів'):
        # step 3
        # Point for visa applications
        try:
            s = self.__browser.find_element_by_xpath(
                '//*[@id="ctl00_plhMain_cboVAC"]')
            # iterate options
            for i in s.find_elements_by_tag_name('option'):
                s = ppva.encode('utf-8')  # convert to bytes
                if i.text.encode('utf-8') == s:
                    i.click()
                    break
        except (NoSuchElementException, Exception) as e:
            print (e)
            logging.error(str(e) + "In register.py code line 103")
            self.__failedToRegister = self.__failedToRegister + 1
            self.__browser.quit()
            wait_between(2, 3)
            self.register()

        try:
            s = self.__browser.find_element_by_xpath(
                '//*[@id="ctl00_plhMain_cboPurpose"]')
            for i in s.find_elements_by_tag_name('option'):
                s = u'Подача документів'.encode('utf-8')  # convert to bytes
                if i.text.encode('utf-8') == s:
                    i.click()
                    break

            # click submit
            self.__browser.find_element_by_xpath(
                '//*[@id="ctl00_plhMain_btnSubmit"]').click()

        except (NoSuchElementException, Exception) as e:
            print str(e)
            logging.error(str(e))
            self.__failedToRegister = self.__failedToRegister + 1
            self.__browser.quit()
            wait_between(2, 3)
            self.register()

        wait_between(6, 7)

    def thirdPage(self, visaCategory=u'Національна Віза'):
        try:
            # step 4
            # number of applicants
            wait_between(7, 8)
            self.__browser.find_element_by_xpath(
                '//*[@id="ctl00_plhMain_tbxNumOfApplicants"]').click()
            self.__browser.find_element_by_xpath(
                '//*[@id="ctl00_plhMain_tbxNumOfApplicants"]').clear()
            self.__browser.find_element_by_xpath(
                '//*[@id="ctl00_plhMain_tbxNumOfApplicants"]').send_keys(str(1))  # fixed always 1
            # Amount of children included in the passport of parents
            self.__browser.find_element_by_xpath(
                '//*[@id="ctl00_plhMain_txtChildren"]').send_keys(str(0))

            # Visa category
            s = self.__browser.find_element_by_xpath(
                '//*[@id="ctl00_plhMain_cboVisaCategory"]')
            for i in s.find_elements_by_tag_name('option'):
                s = visaCategory.encode('utf-8')  # convert to bytes
                if i.text.encode('utf-8') == s:
                    i.click()
                    break
            wait_between(1.5, 2)

        except (NoSuchElementException, Exception) as e:
            print str(e)
            logging.error(str(e))
            self.__failedToRegister = self.__failedToRegister + 1
            self.__browser.quit()
            wait_between(2, 3)
            self.register()

    # solve captcha image challenge
    # get Captchas dimentions - 3*3 or 4*4 or 4*2
    def submitCaptchaForm(self):
        mainWin = self.__browser.current_window_handle  # current window
        self.__browser.switch_to.window(mainWin)
        print 'main window is ', mainWin

        # create captcha object

        cap = Captcha(self.__browser)

        # fill reCaptcha checkbox
        if (cap.selectCheckbox()) == False:
            self.__failedToRegister = self.__failedToRegister + 1
            self.__browser.quit()
            wait_between(2, 3)
            pass
        wait_between(1.5, 2.0)

        # solving Captcha function (extended)
        capIsSolved = cap.Solve()

        if(capIsSolved):  # when captcha solved and ticked
            # submit form
            try:
                wait_between(2, 3)
                self.__browser.find_element_by_xpath(
                    '//*[@id="recaptcha-verify-button"]').click()
                wait_between(1, 3)

                self.__browser.switch_to_default_content()

                # checking for errors in page
                s = self.__browser.page_source

                if 'Повторіть спробу.'.decode('utf-8') in s:
                    self.__failedToRegister = self.__failedToRegister + 1
                    self.__browser.quit()  # exit
                elif 'Виберіть усі зображення, на яких є вказані об’єкти.'.decode('utf-8') in s:
                    self.__failedToRegister = self.__failedToRegister + 1
                    self.__browser.quit()  # exit

                print 'currenct iframe ', self.__browser.current_window_handle
                self.__browser.switch_to_default_content()
                print 'switched to main window ', mainWin

                self.__browser.find_element_by_xpath(
                    '//*[@id="ctl00_plhMain_btnSubmit"]').click()

                logging.info('Passed first captcha!')
                wait_between(3, 4)

                # check if has error
                try:
                    # search for receipt number error
                    s = self.__browser.find_element_by_xpath(
                        '//*[@id="ctl00_plhMain_lblMsg"]/font/font').text

                    if 'No date (s) available for' in s:
                        logging.error(str(s))
                        print ('Date is not available')

                        email.sendNoDateAvailable(self.applicationID)
                        self.__failedToRegister = self.__failedToRegister + 1
                        self.__ExitImmidiatly = True
                        self.__browser.quit()
                        return False

                        # update db
                except:
                    # all good, proceed to next page

                    pass

            except NoSuchElementException as e:
                # if fails start captcha all over again
                print e
                logging.debug(str(e))
                self.__failedToRegister = self.__failedToRegister + 1
                self.__browser.quit()
        else:
            logging.error('Captcha failed, trying once again.')
            # captch fails, try all from the beginning
            print 'CAPTCHA FAILED! Refreshing Captcha'

            addFailureToCaptchaHis(logsPath)

            self.__failedToRegister = self.__failedToRegister + 1
            # switch to first iframe
            self.__browser.implicitly_wait(5)
            self.__browser.quit()
            self.__ExitImmidiatly = True
            return False
            wait_between(2, 3)
            # self.submitCaptchaForm()
        pass

    def evadePopup(self):
        # self.__browser.execute_script('window.location=window.location;')
        pass

    def fourthPage(self, recepientNumber='2333/4444/2222'):
        addSuccessToCaptchaHis(logsPath)

        logging.info('Entered recepient number page')
        # wait implicitly_wait
        wait_between(5, 7)
        try:
              # example
            self.__browser.find_element_by_xpath(
                '//*[@id="ctl00_plhMain_repAppReceiptDetails_ctl01_txtReceiptNumber"]').send_keys(str(recepientNumber))
            self.__browser.find_element_by_xpath(
                '//*[@id="ctl00_plhMain_btnSubmit"]').click()  # submit entered recepient number.
            # if error xpath exists - this means the recepient number is
            # incorrect
            wait_between(5, 6)
            try:
                self.__browser.find_element_by_xpath(
                    '//*[@id="ctl00_plhMain_lblMsg"]')
                # notify operator for that recepient is
                logging.error(
                    'Recepient number {0} is incorrect.'.format(str(recepientNumber)))
                email.sendRecepientError(recepientNumber)
                self.__failedToRegister = self.__failedToRegister + 1
                self.__browser.quit()
                self.__ExitImmidiatly = True
                return False

            except NoSuchElementException:
                # proceed to date page
                logging.info('Reciepent Number is Valid')
                print ('Receipt Number is valid')
                pass

        except NoSuchElementException as e:
            print 'Error with Receipt Number'
            logging.error(
                'Failed to enter recepient number {0}. Reason {1}'.format(str(recepientNumber), str(e)))
            self.__failedToRegister = self.__failedToRegister + 1
            self.__browser.implicitly_wait(5)
            self.__browser.quit()
            self.__ExitImmidiatly = True
            return False

            pass
        pass

    # enter random email and password.
    def fifthPage(self):

        wait_between(2, 3)
        e = randomEmail()
        p = randomPass()

        # insert values into DB

        self.__browser.find_element_by_xpath(
            '//*[@id="ctl00_plhMain_txtEmailID"]').send_keys(str(e))  # email
        self.__browser.find_element_by_xpath(
            '//*[@id="ctl00_plhMain_txtPassword"]').send_keys(str(p))  # password

        # save credentials to db

        #c = Conn()
        #
        #
        #
        #
        #
        #

        # press submit
        self.browser.find_element_by_xpath(
            '//*[@id="ctl00_plhMain_btnSubmitDetails"]').click()

        logging.info('submitted email and password')
        wait_between(4, 5)
        pass

    # filling the application data
    def sixthPage(self):

        print 'filling the application data!'
        pass


for i in range(5):
    s = Register()
    s.startRegisteringApplicant('2096/3788/9676')  # start


# 2096/3788/9676
