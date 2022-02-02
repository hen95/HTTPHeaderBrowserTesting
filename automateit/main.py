from types import ClassMethodDescriptorType
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

import time
import browsers

credentials = "USERNAME:PASSWORD@"
BROWSERSTACK_URL = 'https://' + credentials + 'hub-cloud.browserstack.com/wd/hub'



def checkAlert(driver):
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        return True
    except TimeoutException:
        return False

urls = [
    ["https://much.ninja/XFO/comp/compability.html", 30],
    #["https://much.ninja/XFO/meta/index.html", 10],
    ["https://much.ninja/CSP/meta/csp.html", 10],
    ["https://much.ninja/CSP/duplicated-fa/index.html", 30],
    ["https://much.ninja/CSP/CSPvsXFO/index.html", 20],
    ["http://much.ninja/HSTS/comp/compability.php", 40],
    #["http://much.ninja/HSTS/latest/index.php", 20],
    ["https://much.ninja/CORS/acao.html", 15],
    ["https://much.ninja/CORS/acac.html", 20],
    ["https://much.ninja/CORS/acao-preflight.html", 15],
    ["https://much.ninja/CORS/acac-preflight.html", 20],
    ["https://much.ninja/CORS/acah-preflight.html", 15],
    ["https://much.ninja/CORS/acam-preflight.html", 15],
    ["https://much.ninja/CORS/aceh.html", 10]
    ]

def runtestcase(driver, url, sleeper):
    driver.get(url)

    # start the test
    print(f'''[+] Starting Test {url}''')
    time.sleep(sleeper)

    driver.find_element_by_partial_link_text('Save test').click()
    checkAlert(driver)
    print('[+] Test Done')
    return

def runTest(cap):
    print(f'''[+] Starting browser {cap['os']} {cap['os_version']}, {cap['browser']} {cap['browser_version']}''')

    # start the remote browser
    driver = webdriver.Remote(
        command_executor=BROWSERSTACK_URL,
        desired_capabilities=cap,
        #options=options
    )

    print(f'''[+] https://automate.browserstack.com/dashboard/v2/builds/7004a0c3687f35784951a468064d20cc4dda36f4/sessions/{driver.session_id}''')
    print('[+] Loading stuff')
    
    for entry in urls:
        runtestcase(driver, entry[0], entry[1])

    print('[+] Stopping Browser')
    driver.quit()
    
    return


# run all tests with browsers from browser.py
for i,test in enumerate(browsers.capabilitiesList):
    # enable debugging
    test['browserstack.networkLogs'] = "false"
    test['browserstack.video'] = "false"
    test['browserstack.console'] = "verbose"
    test['loggingPrefs'] = { 'browser':'ALL' }
    try:
        print(f'[+] Starting Test {i+1}/{len(browsers.capabilitiesList)}')
        runTest(test)
    except Exception as e:
        print('[-] Test failed')
        print(e)
