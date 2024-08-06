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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

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
        max_itter = 15
        for _ in range(max_itter):
            posts = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            print(posts)
            
            LatestPost = posts[-1]
            TimePosted = LatestPost.find_element(By.XPATH, ".//time").get_attribute('datetime')
            TimeInDays = TimeZone(TimePosted)
            print("time in days", TimeInDays, "timeframe", time_frame)
            if TimeInDays < time_frame:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                WebDriverWait(driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            else:
                break
            
                

def login(driver):
    driver.get("https://x.com/i/flow/login")
    wait = WebDriverWait(driver, 10)
    
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username"]')))
        username_input = driver.find_element(By.XPATH, '//input[@autocomplete="username"]')
        print("inputing username")
        username_input.send_keys(os.getenv("twitter_email"))
        username_input.send_keys(Keys.ENTER)
        
    except BaseException as e:
        print("could not login, erorr: ", e)
        return 1
        
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
    except BaseException:
        pass
        
        
        
    
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
        password_input = driver.find_element(By.XPATH, '//input[@name="password"]')
        print("inputing password")
        password_input.send_keys(os.getenv("twitter_pass"))
        password_input.send_keys(Keys.ENTER)
    except TimeoutException as e:
        print("could not log in erorr: ", e)
        return 1
    time.sleep(5)
    return 0


def main(twitter_accounts, tickers, time_frame, RedditAccounts):
    # print("setting up driver")
    # service = Service(ChromeDriverManager().install())
    # print("installed driver")
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-extensions")
    # options.add_argument("disable-infobars")
    # print("starting driver")
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
    print("driver start success")
    TickerCount = [0]*len(tickers)
    TickerCommentCount = [0]*len(tickers)

    loged = login(driver)
    if loged == 1:
        return
    #iterate over each account
    wait = WebDriverWait(driver, 10)
    for account in twitter_accounts:
        print("Now scraping", account)
        driver.get(f"https://x.com/{account}")

        try:
            
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
            if not CheckTime(post, time_frame):
                break

            try:
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

    for account in RedditAccounts:
        print("inside", account)
        driver.get(f"https://www.reddit.com/" + account + "/new/")
        

        print("check point")
        ScrolllingTillTimeMeet(time_frame, driver)
        print("check point 2")
        AttachedPosts = 0
        print("collecting posts")
        posts = driver.find_elements(By.XPATH, "//article[@class='w-full m-0']")
        original_window = driver.current_window_handle
        for post in posts:
            print("inside", post)
            if CheckTime(post, time_frame):
                if CheckFlair(post):
                    continue
                else:
                    article = post.find_element(By.XPATH, ".//shreddit-post/a")
                    href = article.get_attribute("href")

                    print("link", href)
    
                    driver.execute_script("window.open(arguments[0]);", href)

                    print("swithching to article")
                    driver.switch_to.window(driver.window_handles[-1]) 
                    PostDetail(driver, AttachedPosts, TickerCount, tickers)
                    PostComments(driver, TickerCount, tickers)
                    driver.close()
                    driver.switch_to.window(original_window)
            else:
                break

        tickerdict = {}
    for i in range(len(tickers)):
        if TickerCount[i] >= 5:
            tickerdict[tickers[i]] = TickerCount[i]
    driver.quit()
    return tickerdict



def CheckTime(post, time_frame):
    TimePosted = post.find_element(By.XPATH, ".//time").get_attribute('datetime')
    TimeInDays = TimeZone(TimePosted)
    if TimeInDays < time_frame:
        return True
    else:
        return False


def PostDetail(driver, AttachedPosts, TickerCount, TickerList):
    try:
        WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, '//div[@class="text-neutral-content"]')))
        text =  driver.find_element(By.XPATH, '//h1[@slot="title"]').text
        text = text + " " + driver.find_element(By.XPATH, '//div[@class="text-neutral-content"]').text
        print(text)

        for i in range(len(TickerList)):
            ticker_patterns = []
            ticker_pattern = re.escape(TickerList[i])
            ticker_patterns.append(r'[$#]?' + r'(["\{\[])?' + ticker_pattern + r'(["\}\]])?\b')

            pattern = re.compile('|'.join(ticker_patterns))
            if re.search(pattern, text):
                TickerCount[i] = TickerCount[i] + 1

        AttachedPosts = AttachedPosts + 1
    except TimeoutException:
        pass

def PostComments(driver, TickerCommentCount, TickerList):
    comments = driver.find_elements(By.XPATH, '//*[@id="comment-tree"]/shreddit-comment/div[@slot="comment"]')
    for i in range(len(comments)):
        CommentText = comments[i].text
        for i in range(len(TickerList)):
            pattern = fr'\b{re.escape(TickerList[i])}\b'
            if re.search(pattern, CommentText):
                TickerCommentCount[i] = TickerCommentCount[i] + 1

def CheckFlair(post):
    FlairClass = post.find_element(By.XPATH, ".//shreddit-post-flair")
    if "Meme" in FlairClass.text or "MEME" in FlairClass.text or "meme" in FlairClass.text:
        return True
    else:
        return False
    
def ScrolllingTillTimeMeet(time_frame, driver):
    try:
        WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//article[@class='w-full m-0']")))
    except:
        return
    while True:
        posts = driver.find_elements(By.XPATH, "//article[@class='w-full m-0']")
        try:
            LatestPost = posts[-1]
            TimePosted = LatestPost.find_element(By.XPATH, ".//time").get_attribute('datetime')
            TimeInDays = TimeZone(TimePosted)
            print("time in days", TimeInDays, "timeframe", time_frame)
            if TimeInDays < time_frame:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            else:
                break
        except:
            continue