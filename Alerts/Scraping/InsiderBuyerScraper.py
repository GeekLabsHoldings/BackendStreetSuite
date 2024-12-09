from bs4 import BeautifulSoup
from datetime import datetime
import requests
import gzip 
# scraping method for short interest value ##
def insider_buyers_scraper():
    symbols = []

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    } 
    url = "https://finviz.com/insidertrading.ashx?tc=7"
    response = requests.get(url=url, headers=headers)
    try:
        # Check for compression and decompress if needed
        if response.headers.get('Content-Encoding') == 'gzip':
            content = gzip.decompress(response.content).decode('utf-8')
        else:
            # If the content isn't gzipped, just use response.text
            content = response.text
    except (OSError, gzip.BadGzipFile) as e:
        # Handle case where gzip decompression fails
        content = response.text
        
    soup = BeautifulSoup(content, 'html.parser')
    now = datetime.now()
    rows = soup.find_all('tr')
    for row in rows:
        try:
            # Find the <a> tag containing "sec.gov" in the href attribute
            link = row.find('a', href=lambda href: href and 'sec.gov' in href)
            if link and str(now.day) in link.text:
                # Find the <a> tag containing "quote" in the href attribute
                symbol = row.find('a', href=lambda href: href and 'quote' in href)
                if symbol:
                    symbols.append(symbol.text)
        except Exception as e:
            print({"error": e})
    unique_symbols = list(set(symbols))  
    return unique_symbols

        