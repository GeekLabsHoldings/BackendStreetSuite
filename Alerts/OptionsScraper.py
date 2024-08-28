from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

## method of earning scrapping ##
def earning_scraping(ticker_symbol):
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
    driver.get(f"https://tools.optionsai.com/earnings/{ticker_symbol}")
    sleep(5)
    ## get advertisement if its exists ##
    try:
        close_button = driver.find_element(By.XPATH , '//button[@class="MuiButtonBase-root MuiIconButton-root jss237"]') 
        sleep(5)
        close_button.click()
        sleep(3)

    except:
        ...
    finally:
        try:
            ## find paragraph element that has an expected moves value ##
            paragraph_element = driver.find_elements(By.XPATH,'//p[@class="MuiTypography-root jss142 jss145 jss144 MuiTypography-body1"]')[1]
            ## get the text inside it ##
            expected_moves_text = paragraph_element.text
            driver.close()
            return expected_moves_text
        except:
            driver.close()
        
