from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def main(TickerList):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    chromedriver_path = '/usr/local/bin/chromedriver-linux64/chromedriver'
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    print("driver executed")

        # Getting tickers 
    
    RedditAccounts =["r/wallstreetbets", "r/shortsqueeze"]

    TickerCount = {ticker.symbol: 0 for ticker in TickerList}
    for account in RedditAccounts:
        driver.get(f"https://www.reddit.com/" + account + "/new/")
        print(f"scraping {account}")
        previous_posts = []
        # presence of the account without scrolling
        try:
            WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//article[@class='w-full m-0']")))
        except Exception as e:
            return ({"error": e})
        f = True
        # finding the posts with scrolling
        while True:
            posts = driver.find_elements(By.XPATH, "//article[@class='w-full m-0']")
            print(f"the length of posts = {len(posts)}")
            for post in posts:
                if f:
                    previous_posts.append(post)
                    f = False
                    continue
                if post not in previous_posts:
                    FlairClass = post.find_element(By.XPATH, ".//shreddit-post-flair").text
                    if "Meme" in FlairClass or "MEME" in FlairClass or "meme" in FlairClass:
                        print("meme")
                        continue
                    print(f"FlairClass: {FlairClass}")
                    TimePosted = post.find_element(By.TAG_NAME ,"time").text
                    hour = int(TimePosted.split()[0])
                    #check the time of post before entering it
                    if (hour < 23 or "min." in TimePosted) and "day" not in TimePosted:
                        article = post.find_element(By.XPATH, ".//shreddit-post/a")
                        # opening a new tab and switching to it
                        href = article.get_attribute("href")
                        driver.execute_script("window.open(arguments[0]);", href)
                        driver.switch_to.window(driver.window_handles[-1])
                        # collecting data from post
                        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                        text =  driver.find_element(By.XPATH, '//h1[@slot="title"]').text
                        try:
                            text2 = driver.find_element(By.XPATH, '//div[@class="text-neutral-content"]').text
                        except:
                            text2 = ""
                        text = text + " " + text2
                        for ticker in TickerList:
                            # Construct the regex pattern to match the ticker with symbols
                            ticker_pattern = r'[$#]?[\{\[]?' + re.escape(ticker.symbol) + r'[\}\]]?\b'
                            pattern = re.compile(ticker_pattern)
                            # If the ticker is found, increment its count in the dictionary
                            if pattern.search(text):
                                TickerCount[ticker.symbol] += 1        
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        previous_posts.append(post)
                        print("collected")
                    else:
                        break
            LatestPost = posts[-1]
            TimePosted = LatestPost.find_element(By.TAG_NAME ,"time").text
            hour = int(TimePosted.split()[0])
            if (hour < 23 or "min." in TimePosted) and "day" not in TimePosted:
                print("scrolling")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            else: 
                break
    driver.close()
    return(TickerCount)
