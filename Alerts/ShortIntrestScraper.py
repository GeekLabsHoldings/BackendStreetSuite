from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
import pytz
import re
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

tickers = ["NVDA", "TSLA"]
def main():


    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--no_sandbox")

    # Use the specified ChromeDriver binary path
    service = Service(ChromeDriverManager("125.0.6422.113").install())
    driver = webdriver.Chrome(service=service, options=options)

    value_dict = {}
    for i in range(len(tickers)):

        driver.get(f"https://www.benzinga.com/quote/{tickers[i]}/short-interest")
        
        WebDriverWait(driver, 15).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@class="card-value font-extrabold"]')))
        value = driver.find_elements(
            By.XPATH, '//div[@class="card-value font-extrabold"]')

        value_dict[tickers[i]] = value[1].text
    return value_dict
