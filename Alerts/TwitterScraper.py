import time
import re
import sched
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import sys
import pytz
from datetime import datetime
from selenium.webdriver.common.keys import Keys
import os
from dotenv import load_dotenv


load_dotenv()

def TimeZone(time):
    timestamp = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    timestamp_utc = timestamp.replace(tzinfo=pytz.utc)
    
    cairo_timezone = pytz.timezone('UTC')

    timestamp_cairo = timestamp_utc.astimezone(cairo_timezone)
   
    current_time_cairo = datetime.now(cairo_timezone)

    time_difference = current_time_cairo - timestamp_cairo

    day_difference = float(time_difference.total_seconds() / 86400)
    return day_difference

def scrape_ticker_mentions(driver, TickerCount, tickers):
    
    try:
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="tweetText"]')))   # wait for page to load
    except TimeoutException:
        print("article text element not found")
        return
    text = driver.find_element(
            By.XPATH, '//div[@data-testid="tweetText"]').text
    print(text)

    for i in range(len(tickers)):
            ticker_patterns = []
            ticker_pattern = re.escape(tickers[i])
            ticker_patterns.append(r'\b[$#]?' + r'(["\{\[])?' + ticker_pattern + r'(["\}\]])?\b')

            pattern = re.compile('|'.join(ticker_patterns), re.IGNORECASE)
            
            if re.search(pattern, text):
                print("FOUND", tickers[i])
                TickerCount[i] += 1
            else:
                print("no match")
    
       

def scrolltilltime(time_frame, driver):
        print("aaaaaaaaaa")
        while True:
            posts = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            print(posts)
            try:
                LatestPost = posts[-1]
                TimePosted = LatestPost.find_element(By.XPATH, ".//time").get_attribute('datetime')
                TimeInDays = TimeZone(TimePosted)
                print("time in days", TimeInDays, "timeframe", time_frame)
                if TimeInDays < time_frame:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    WebDriverWait(driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                else:
                    break
            except:
                continue

def login(driver):
    driver.get("https://x.com/i/flow/login")
    wait = WebDriverWait(driver, 10)
    
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username"]')))
        username_input = driver.find_element(By.XPATH, '//input[@autocomplete="username"]')
        print("inputing username")
        username_input.send_keys(os.getenv("twitter_email"))
        username_input.send_keys(Keys.ENTER)
        
    except TimeoutException:
        sys.exit("could not log in")
        
    time.sleep(3)

    try:
        driver.find_element(By.XPATH, '//input[@data-testid="ocfEnterTextTextInput"]')
        print("inputing username again")

        username_input = driver.find_element(By.XPATH, '//input[@data-testid="ocfEnterTextTextInput"]')
        username_input.send_keys(os.getenv("twitter_user"))
        username_input.send_keys(Keys.ENTER)
        time.sleep(2)
        if driver.find_element(By.XPATH, '//input[@autocomplete="username"]'):
            username_input.send_keys(os.getenv("twitter_email"))
            username_input.send_keys(Keys.ENTER)
    except NoSuchElementException:
        pass
        
        
        
    
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
        password_input = driver.find_element(By.XPATH, '//input[@name="password"]')
        print("inputing password")
        password_input.send_keys(os.getenv("twitter_pass"))
        password_input.send_keys(Keys.ENTER)
    except TimeoutException:
        sys.exit("could not log in")

    time.sleep(5)


def main(twitter_accounts, tickers, time_frame):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=options)
    TickerCount = [0]*len(tickers)
    login(driver)
    #iterate over each account
    for account in twitter_accounts:
        print("Now scraping", account)
        driver.get(f"https://x.com/{account}")

        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))
        except TimeoutException:
            print("timed out while waiting for tweets to load for", account)
            continue
        print("in account", account)
        time.sleep(3) 
        scrolltilltime(time_frame, driver)
        posts = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        original_window = driver.current_window_handle
        print("collected posts")
        for post in posts:
            # if not CheckTime(post):
            #     break

            try:
                wait = WebDriverWait(driver, 9)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.css-175oi2r.r-18u37iz.r-1q142lx > a')))
                article = post.find_element(By.CSS_SELECTOR, 'div.css-175oi2r.r-18u37iz.r-1q142lx > a')
            except:
                continue

            href = article.get_attribute("href")
            driver.execute_script("window.open(arguments[0]);", href)

            print("swithching to article")
            driver.switch_to.window(driver.window_handles[-1])
            print("scraping article")
            scrape_ticker_mentions(driver, TickerCount, tickers)

            print("closing article window")
            driver.close()
            print("swtiching windows")
            driver.switch_to.window(original_window)

    for i in range(len(tickers)):
        print(f"The ticker '{tickers[i]}' appears {TickerCount[i]} time(s)")

        tickerdict = {}
    for i in range(len(tickers)):
        if TickerCount[i] >= 5:
            tickerdict[tickers[i]] = TickerCount[i]
    
    tickerdict["SPY"] = 7
    return tickerdict



def CheckTime(post):
    TimePosted = post.find_element(By.XPATH, ".//time").get_attribute('datetime')
    TimeInDays = TimeZone(TimePosted)
    if TimeInDays < time_frame:
        return True
    else:
        return False


time_frame = .25

