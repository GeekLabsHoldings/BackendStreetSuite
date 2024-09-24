from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from Alerts.models import Alert
from .consumers import WebSocketConsumer
from selenium.webdriver.support import expected_conditions as EC
# scraping method for short interest value ##
def short_interest_scraper(tickers):
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    chromedriver_path = '/usr/bin/chromedriver'
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    # symbols that have short-interest values
    symbols = []
    # looping on each ticker
    for ticker in tickers:
    ## open url on the web driver ##
        print(f"short interest {ticker.symbol}")
        driver.get(f'https://www.benzinga.com/quote/{ticker.symbol}/short-interest')
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        ## check if advertisement is exists or not ##
        try :
            close_button = driver.find_element(By.XPATH,'//button[@class="CloseButton__ButtonElement-sc-79mh24-0 gkmgjx basslake-CloseButton basslake-close basslake-ClosePosition--top-right"]')
            close_button.click()
        except:
            ...
        finally:
            try:
                ## get element of value of short interest ##
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="card-value font-extrabold"]')))
                value = driver.find_elements(By.XPATH, '//div[@class="card-value font-extrabold"]')
                value_text = value[1].text
                print(value_text)
                if '-' not in value_text:
                    value_string = value_text.strip("%")
                    float_value = float(value_string)
                    # if the value is greater than or equal to 30 then create a new alert
                    if float_value >=30:
                            alert = Alert.objects.create(ticker=ticker,strategy='Short Interest',result_value=float_value)
                            alert.save()
                            WebSocketConsumer.send_new_alert(alert)
                            symbols.append(ticker.symbol)
            except Exception as e :
                print(ticker.symbol)
                print({"error": e})
                continue         
    #closing the driver after finishing scraping         
    driver.close()
    return symbols    