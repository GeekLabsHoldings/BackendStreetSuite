from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def main(tickers):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--no_sandbox")
    driver = webdriver.Chrome(service=service, options=options)

    # get ticer website
    # print("getting ticker website")

    value_dict = {}
    for i in range(len(tickers)):
        driver.get(f"https://tools.optionsai.com/earnings/{tickers[i]}")
        # print("on ticker number", i)
        if i == 0:
            try:
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained jss264 jss255 MuiButton-containedPrimary MuiButton-disableElevation"]')))
                button = driver.find_element(By.XPATH, '//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained jss264 jss255 MuiButton-containedPrimary MuiButton-disableElevation"]')
                button.click()
            except TimeoutException or NoSuchElementException:
                pass


        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//p[@class="MuiTypography-root jss142 jss145 jss144 MuiTypography-body1"]')))
            # print("found expected moves")
            sleep(10)
            value = driver.find_elements(By.XPATH, '//p[@class="MuiTypography-root jss142 jss145 jss144 MuiTypography-body1"]')[1].text
            print(value)
            value_dict[tickers[i]] = value
        except BaseException:
            continue
        

    driver.close()
    return value_dict
