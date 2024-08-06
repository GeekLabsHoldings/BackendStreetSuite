from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# def main(tickers):
    # service = Service(ChromeDriverManager().install())
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-extensions")
    # options.add_argument("disable-infobars")
    # driver = webdriver.Chrome(service=service, options=options)

#     # get ticer website
#     # print("getting ticker website")

#     value_dict = {}
#     for i in range(len(tickers)):
#         driver.get(f"https://tools.optionsai.com/earnings/{tickers[i]}") 
#         # print("on ticker number", i)
#         if i == 0:
#             try:
#                 WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained jss264 jss255 MuiButton-containedPrimary MuiButton-disableElevation"]')))
#                 button = driver.find_element(By.XPATH, '//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained jss264 jss255 MuiButton-containedPrimary MuiButton-disableElevation"]')
#                 button.click()
#             except TimeoutException or NoSuchElementException:
#                 pass


#         try:
#             WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//p[@class="MuiTypography-root jss142 jss145 jss144 MuiTypography-body1"]')))
#             # print("found expected moves")
#             sleep(15)
#             value = driver.find_elements(By.XPATH, '//p[@class="MuiTypography-root jss142 jss145 jss144 MuiTypography-body1"]')[1].text
#             print(value)
#             value_dict[tickers[i]] = value
#         except BaseException:
#             continue
        

#     driver.close()
#     return value_dict

## method of earning scrapping ##
def earning_scraping(ticker_symbol):
    # print(ticker_symbol)
    # service = Service(ChromeDriverManager().install())
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-extensions")
    # options.add_argument("disable-infobars")
    # driver = webdriver.Chrome(service=service, options=options)
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
        print("found")
        sleep(5)
        close_button.click()
        print("clicked")
        sleep(3)

    except:
        ...
    finally:
        try:
            ## find paragraph element that has an expected moves value ##
            paragraph_element = driver.find_elements(By.XPATH,'//p[@class="MuiTypography-root jss142 jss145 jss144 MuiTypography-body1"]')[1]
            ## get the text inside it ##
            expected_moves_text = paragraph_element.text
            print(expected_moves_text) 
            print(type(expected_moves_text)) 
            driver.close()
            return expected_moves_text
        except:
            print("not exists")
            driver.close()
        
