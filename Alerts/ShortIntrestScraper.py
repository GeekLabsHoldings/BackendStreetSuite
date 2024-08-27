from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
import pytz
import re
from selenium.webdriver.chrome.service import Service
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# scraping method for short interest value ##
def short_interest_scraper(ticker_symvol):
    print(ticker_symvol)
    
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    chromedriver_path = '/usr/local/bin/chromedriver-linux64/chromedriver'
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    sleep(5)
    ## open url on the web driver ##
    driver.get(f'https://www.benzinga.com/quote/{ticker_symvol}/short-interest')
    sleep(5)
    ## check if advertisement is exists or not ##
    try :
        close_button = driver.find_element(By.XPATH,'//button[@class="CloseButton__ButtonElement-sc-79mh24-0 gkmgjx basslake-CloseButton basslake-close basslake-ClosePosition--top-right"]')
        # print('found x')
        close_button.click()
        # print("clicked")
        sleep(5)
    except:
        ...
    finally:
        ## get element of value of short interest ##
        value = driver.find_elements(By.XPATH, '//div[@class="card-value font-extrabold"]')
        sleep(3)
        # print("found element")
        try:
            value_text = value[1].text
            sleep(2)
            # print(value_text)
            value_string = value_text.strip("%")
            float_value = float(value_string)
            driver.close()
            return float_value
            # print(type(float_value))
        except:
            return 0
            # print("nothing")