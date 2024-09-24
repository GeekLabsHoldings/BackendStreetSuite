from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
# scraping method for short interest value ##
def insider_buyers_scraper():
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    chromedriver_path = '/usr/bin/chromedriver'
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    symbols = []

    driver.get("https://finviz.com/insidertrading.ashx?tc=7")
    WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    rows = driver.find_elements(By.XPATH, "//tr")
    for row in rows:
        try:
            link = row.find_element(By.XPATH, './/a[contains(@href, "sec.gov")]')
            now = datetime.now()
            if str(now.day) in link.text:
                symbol = row.find_element(By.XPATH, './/a[contains(@href, "quote")]')
                symbols.append(symbol.text)
            else:
                continue
        except Exception as e:
            print({"error" : e })
    unique_symbols = list(set(symbols))
    return unique_symbols

        