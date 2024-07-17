from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
import pytz
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def main(ticker):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--no_sandbox")
    driver = webdriver.Chrome(options=options)

    # get ticer website
    print("getting ticker website")
    driver.get(f"https://tools.optionsai.com/earnings/{ticker}")
  
    sleep(5)
    try:
        button = driver.find_element(By.XPATH, '//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained jss264 jss255 MuiButton-containedPrimary MuiButton-disableElevation"]')
        button.click()
    except NoSuchElementException:
        pass
    
    sleep(1)
    text = driver.find_elements(By.XPATH, '//p[@class="MuiTypography-root jss142 jss145 jss144 MuiTypography-body1"]')[1].text
    return text
    driver.close()

main("TSLA")