import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from ..models import Ticker
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from Alerts.models import Alert , Ticker
from ..consumers import WebSocketConsumer

# Set up headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

## method to get sumbols and appeand them ##
def get_symbols(url,symbol_list):
    ## request on the url ##
    response = requests.get(url=url , headers=headers)
    ## get html content soup ##
    soup = BeautifulSoup(response.text, 'html.parser')
    ## get all symbols ##
    symbols = soup.find_all('a',class_="tab-link")
    ## get symbols ##
    for symbol in symbols:
        symbol_list.append(symbol.text)
    return symbol_list

## method to click on next button if exists ##
def go_next(driver , symbol_list):
    ## chcek if next button for pagination is exists or not ##
    try:
        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@class="screener-pages is-next"]')))
        button.click()
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        url = driver.current_url
        symbol_list = get_symbols(url=url, symbol_list=symbol_list)
        driver , symbol_list = go_next(driver=driver , symbol_list=symbol_list)
        return driver ,symbol_list
    except:
        return driver , symbol_list

## main method ##
def short_interest_scraper_tickers():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    chromedriver_path = '/usr/bin/chromedriver'
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service , options=options)
    # driver = webdriver.Chrome()
    driver.get("https://finviz.com/screener.ashx?v=111&f=geo_usa,sh_short_o30&ft=4&o=ticker")
    # get the url #
    url = driver.current_url
    # request on  the url #
    response1 = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response1.text , 'html.parser')
    symbol_list = []
    ## get symbols ##
    symbols = soup.find_all('a',class_="tab-link")
    for symbol in symbols:
        symbol_list.append(symbol.text)
    driver , symbol_list = go_next(driver=driver , symbol_list=symbol_list)
    driver.close()
    symbol_list = set(symbol_list)
    return symbol_list

def short_interest_scraper():
    symbol_list = short_interest_scraper_tickers()
    ########### start request by BS ##########
    for symbol in symbol_list:
        response = requests.get(f"https://www.benzinga.com/quote/{symbol}/short-interest/")

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            # Example: Find the section containing the short interest data
            # This step requires inspecting the HTML structure of the page.
            short_interest_section = soup.find_all('div', class_='card-value font-extrabold')
            
            # Extract text or specific data from the section
            if short_interest_section:
                short_interest_data = short_interest_section[1].get_text(strip=True)
                ## check if could create alerts or not  
                try:
                    value = float(short_interest_data[:-1])
                    if value >= 30.0:
                        ticker = Ticker.objects.get(symbol= symbol)
                        alert = Alert.objects.create(ticker=ticker,result_value=value,strategy='Short Interest',risk_level='Bearish')
                        alert.save()
                        WebSocketConsumer.send_new_alert(alert)
                except :
                    continue

        elif response.status_code == 429:
            time.sleep(60)
            value = short_interest_scraper(symbol)
