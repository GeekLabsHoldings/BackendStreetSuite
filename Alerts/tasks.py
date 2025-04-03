import requests, time
from Alerts.models import Ticker ,  Alert
from celery import shared_task, chain
from .consumers import WebSocketConsumer
from django.core.cache import cache
from datetime import datetime, timedelta
############# import scraping ################
from .Scraping.TwitterScraper import twitter_scraper
from .Scraping.ShortIntrestScraper  import short_interest_scraper
################# import strategies #########################
from .Strategies.RSI import GetRSIStrategy
from .Strategies.EMA import GetEMAStrategy
from .Strategies.Earnings import GetEarnings
from .Strategies.MajorSupport import GetMajorSupport
from .Strategies.RelativeVolume import GetRelativeVolume
from .Strategies.insider_buyer import GetInsider_Buyer
from .Strategies.UnusualOptionBuys import GetUnusualOptionBuys
from .Strategies.Get13F import Get13F
from .Strategies.StrikeOption import GetStrike
from .Strategies.RSINew import fetch_rsi_data
from .Strategies.TradersQuotes import GetTraderQuotes


def get_cached_queryset():
    queryset_data = cache.get("tickerlist")
    
    if queryset_data is None or not isinstance(queryset_data, list):
        excluded_symbols = [
        "ACI", "ACM", "AFG", "AFRM", "AGNCL", "AGNCM", "AGNCN", "AGNCO", "AGNCP", "AGR", "ALLY", "ALNY",
        "AMH", "APO", "APOS", "APP", "AQNB", "ARES", "ARCC", "ARMK", "ATR", "AVTR", "AZPN", "BAH", "BEPC",
        "BJ", "BLD", "BMRN", "BKDT", "BSY", "BURL", "CACI", "CASY", "CAVA", "CCZ", "CET", "CG", "CCK",
        "CHDN", "CHWY", "CLH", "CNA", "COHR", "COIN", "COKE", "CPNG", "CSL", "CQP", "CRBG", "CUBE", "CUK",
        "CVNA", "CW", "DELL", "DKNG", "DKS", "DOCU", "DT", "DUKB", "EDR", "ELS", "EME", "ENTG", "EPD",
        "EQH", "ERIE", "ET", "EWBC", "EXAS", "FCNCA", "FITBI", "FITBO", "FITBP", "FIX", "FND", "FNF",
        "FTAI", "FTS", "FWONA", "FWONK", "GDDY", "GGG", "GLPI", "GWRE", "H", "HBANL", "HBANM", "HBANP",
        "HEI", "HLI", "HOOD", "HUBS", "IBKR", "INSM", "IOT", "ITT", "JEF", "JLL", "KKR", "KNSL", "LAMR",
        "LII", "LINE", "LNG", "LOGI", "LPLA", "MANH", "MEDP", "MKL", "MORN", "MPLX", "MSTR", "MUSA",
        "NBIX", "NET", "NIO", "NLY", "NTNX", "NTRA", "OC", "OHI", "OKTA", "OWL", "PAA", "PARAA", "PCVX",
        "PFGC", "PINS", "PLTR", "PR", "PSN", "PSTG", "QRTEP", "RBLX", "REXR", "RGA", "RIVN", "RKT",
        "ROKU", "RPM", "RPRX", "RS", "RTO", "RYAN", "SAIA", "SCCO", "SCI", "SE", "SFM", "SLMBP", "SMMT",
        "SN", "SNAP", "SNOW", "SOJC", "SOJD", "SOJE", "SQ", "SREA", "SRPT", "SSNC", "SUI", "SYM", "TBB",
        "TBC", "TELZ", "THC", "TKO", "TME", "TOL", "TOST", "TPG", "TPL", "TRI", "TRU", "TTEK", "TVE",
        "TW", "TXRH", "UHAL", "UI", "USFD", "UTHR", "UWMC", "VEEV", "VLYPO", "VLYPP", "VRT", "WES",
        "WING", "WLK", "WMG", "WMS", "WPC", "WSM", "WSO", "WTRG", "XPO", "YUMC", "Z", "ZG", "ZM"
    ]

        queryset = (
        Ticker.objects
        .filter(market_capital__in=["Mega", "Large"])
        .exclude(symbol__in=excluded_symbols)
        .values("id", "symbol", "market_capital")
    )
        queryset_data = list(queryset)  
        cache.set("tickerlist", queryset_data, timeout=86400)  # Store only list of dictionaries

    return queryset_data 
## method to get data of ticker by api ##
def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    return data.json()


# ######## COMMON METHOD FOR COMMON ALERTS #########
def common(timeframe,applied_function):
    all_tickers = get_cached_queryset()
    print("new loop")
    ct= 0
    for ticker in all_tickers:
        ct += 1
        message = ''
        print(ticker["symbol"])
        # alert = applied_function(ticker, timeframe)
        result = fetch_rsi_data(ticker["symbol"])
        
# Check if the result is valid before unpacking
        if result[0] != 'Unknown':
            risk_level, ticker_price, rsi_value = result
            today = datetime.today().date()

            # Calculate the future date (30 days ahead)
            future_date = today + timedelta(days=30)

            # Check if the future date is a Friday; if not, find the next Friday
            if future_date.weekday() != 4:  # 4 represents Friday
                days_until_friday = (4 - future_date.weekday()) % 7
                future_date += timedelta(days=days_until_friday)

            formatted_future_date = future_date.strftime("%y%m%d")
            ticker_price= int(ticker_price)
            if risk_level == 'Bearish':
                bid_price = GetTraderQuotes(ticker["symbol"], formatted_future_date,'P', ticker_price )
                # options = GetUnusualOptionBuys(ticker, future_date)
                message = (
                f"Option Type = Put Buy / Option Strike = {ticker_price} / "
                f"Option Expiry = {future_date} / Entry price = {bid_price} / "
                f"RSI 5min = {rsi_value[0]} / "
                f"RSI 1hour = {rsi_value[1]} / "
                f"RSI 4hours = {rsi_value[2]} / "
                f"RSI 1day = {rsi_value[3]} / "
            )
                   
            elif risk_level == 'Bullish':
                bid_price = GetTraderQuotes(ticker["symbol"], formatted_future_date,'C', ticker_price )
                # options = GetUnusualOptionBuys(ticker, future_date)
                message = (
                f"Option Type = Call Buy / Option Strike = {ticker_price} / "
                f"Option Expiry = {future_date} / Entry price = {bid_price} / "
                f"RSI 5min = {rsi_value[0]} / "
                f"RSI 1hour = {rsi_value[1]} / "
                f"RSI 4hours = {rsi_value[2]} / "
                f"RSI 1day = {rsi_value[3]} / "
            )
            ticker = Ticker.objects.get(symbol=ticker["symbol"])
            if ct == 30:
                time.sleep(1)
                ct = 0
            try:
                alert = Alert.objects.create(ticker=ticker, strategy='New Alert',
                                             result_value=1,
                                            investor_name=message,
                                            risk_level=risk_level,
                                            )
                alert.save()
                print(f'alert{ticker.symbol}' )
                WebSocketConsumer.send_new_alert(alert)
            except Exception as e:
                print(f'duplication')
                continue

                 
@shared_task(queue='celery_5mins')
def tasks_5mins():
    # common(timeframe='5mins',applied_functions=[GetRSIStrategy])
    common(timeframe='5mins',applied_function=GetRSIStrategy)


