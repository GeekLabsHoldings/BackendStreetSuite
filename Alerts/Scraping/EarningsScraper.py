from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## method of earning scrapping ##
def earning_scraping(ticker_symbol):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    chromedriver_path = '/usr/bin/chromium'
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(f"https://tools.optionsai.com/earnings/{ticker_symbol}")
    ## get advertisement if its exists ##
    try:
        close_button = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH , '//button[@class="MuiButtonBase-root MuiIconButton-root jss237"]')))
        close_button.click()
    except:
        pass
    finally:
        try:
            ## find paragraph element that has an expected moves value ##
            paragraph_elements = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH,'//p[@class="MuiTypography-root jss142 jss145 jss144 MuiTypography-body1"]')))
            paragraph_element_first  = paragraph_elements[1]
            ## get the text inside it ##
            expected_moves_text = paragraph_element_first.text
            print(f"expected_moves_text:{expected_moves_text}")
            driver.close()
            return expected_moves_text
        except:
            print("not found")
            driver.close()
            return None
        
