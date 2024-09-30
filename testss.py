# import http.client

# conn = http.client.HTTPSConnection("api.unusualwhales.com")

# headers = {
#     'Accept': "application/json, text/plain",
#     'Authorization': "Bearer a4c1971d-fbd2-417e-a62d-9b990309a3ce"
# }

# conn.request("GET", "/api/option-contract/NVDA240726C00055000/flow", headers=headers)

# res = conn.getresponse()
# data = res.read()

# print(data.decode("utf-8"))

# from datetime import datetime , timedelta

# day = str(datetime.today() - timedelta(days=30))
# # print(type(day))
# # print(day.date())

# tomorrow = '2024-07-30 00:00:00'
# date_format = "%Y-%m-%d %H:%M:%S"

# date_object = datetime.strptime(tomorrow, date_format)

# from datetime import  datetime  , timezone
# time_now_utc = datetime.now(timezone.utc)
# print(time_now_utc)

# dict1 = {
#     "asem":1,
#     "body":2,
#     "yoyo":5,
#     "weza":8
# }
# dict2 = {
#     "soso":5,
#     "weza":4,
#     "noran":9
# }

# # print(dict2)
# for key , value in dict1.items() :
#     if value > 2:
#         print("yes")

# print(dict2)

# import csv

# # Path to your input and output CSV files
# input_file = 'input.csv'
# output_file = 'output.csv'

# # Open the input file for reading and the output file for writing
# with open(input_file, 'r', newline='') as csv_in, open(output_file, 'w', newline='') as csv_out:
#     reader = csv.reader(csv_in)
#     writer = csv.writer(csv_out)
    
#     # Write the header to the output file
#     header = next(reader)
#     writer.writerow(header)
    
#     # Iterate over rows in the input file
#     for row in reader:
#         # Check if any column in the row contains the '^' character
#         if '^' not in ''.join(row):
#             # If no column contains '^', write the row to the output file
#             writer.writerow(row)

# print("Rows without '^' have been saved to", output_file)

# import csv

# # Path to your CSV file
# input_file = 'output.csv'

# # Open the input file for reading
# with open(input_file, 'r', newline='') as csv_file:
#     reader = csv.reader(csv_file)
    
#     # Loop through each row in the CSV file
#     for row_num, row in enumerate(reader, start=1):
#         print(row[4].strip())
#         # print(row)

# # Open the input file for reading
# with open(input_file, 'r', newline='') as csv_file:
#     reader = csv.reader(csv_file)

#     # Get the header (first row) to identify column names
#     header = next(reader)
#     print(header)
    
#     # Convert rows to columns (transpose the data)
#     columns = list(zip(*reader))
#     listy = []
#     # Loop through each column
#     for i, column in enumerate(columns):
#         if i == 4:
#             for value in column:
#                 listy.append(value)
#             print("length of list",len(listy))
#             sorty = set(listy)
#             sorty.remove('')
#             print(sorty)
#             print("len of set",len(sorty))
            # print()  # Add an empty line after each column for clarity

# l = ['save as portfolio', 'ADV','ABR','create alert', 'ABR', 'ACDC', 'ADV']
# l = set(l)
# print(l)

# from datetime import datetime

# today = datetime.today().date()
# print(today)
# print(type(today))
# from collections import defaultdict

# dicty = {
#     "AAPL":{"strategy":"rsi","value":55},
#     "AAPL":{"strategy":"ema","value":35},
#     "TSLA":{"strategy":"EMA","value":65},
#     "TSLA":{"strategy":"EMA","value":55},
#     "TSLA":{"strategy":"major","value":45},
#     "TSLA":{"strategy":"major","value":55},
# }
# dicty = {
#     "AAPL":{
#             "strategy":"rsi","value":55,
#             "strategy":"ema","value":35
#             },
#     "TSLA":{
#             "strategy":"EMA","value":65,
#             "strategy":"EMA","value":55,
#             "strategy":"major","value":45,
#             "strategy":"major","value":55
#             }
# }

# new_dict = defaultdict(list)
# new_dict["AAPL"].append({"TSLA":"HIGH"})
# new_dict["NVDA"].append({"TSLA":"LOW"})
# new_dict["QQQ"].append({"TSLA":"HIGH"})
# print(new_dict.items())



# ## caching the alerts of the same day ##
# def alerts_today(key_name):
#     queryset = cache.get(f"TodayAlerts_{key_name}")
#     if not queryset:
#         queryset = defaultdict(list)
#         cache.set(f"TodayAlerts_{key_name}", queryset, timeout=86400)
#     else:
#         # If it's retrieved as a normal dict, convert it back to defaultdict
#         queryset = defaultdict(list, queryset)
#     return queryset
# ## rsi function ##
# def rsi(timespan):
#     tickers = get_cached_queryset()
#     ## initialize results parameters ##
#     result_strategy = Result.objects.get(strategy='RSI',time_frame=timespan)
#     result_success = 0
#     result_total = 0
#     i = 0
#     for ticker in tickers[800:900]:
#         i += 1
#         print(f"RSI {timespan},{i}")
#         risk_level = None
#         ticker_price = None
#         result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
#         if result != []:
#             print(ticker.symbol)
#             try:
#                 rsi_value = result[0]['rsi']
#                 ticker_price = result[0]['close']
#                 previous_value = result[1]['rsi']
#                 previous_price = result[1]['close']
#             except BaseException:
#                 continue
#             # to calculate results of strategy success according to current price ##
#             if (
#                 (previous_value > 70 and previous_price > ticker_price) or 
#                 (previous_value < 30 and previous_price < ticker_price)
#             ):
#                 result_success += 1
#                 result_total += 1
#             else:
#                 result_total += 1
#             # Creating the Alert object and sending it to the websocket
#             if rsi_value > 70:
#                 risk_level = 'Bearish'
#             if rsi_value < 30:
#                 risk_level = 'Bullish'
#             if risk_level != None:
#                 try:
#                     caching = alerts_today(key_name=timespan)
#                     print("caching rsi" , caching)
#                     caching[f'{ticker.symbol}'].append({"strategy":"RSI","value":rsi_value,"risk level":risk_level})
#                     cache.set(f"TodayAlerts_{timespan}", caching, timeout=86400)
#                     alert = Alert.objects.create(ticker=ticker , strategy= 'RSI' ,time_frame=timespan ,risk_level=risk_level , result_value = rsi_value , current_price = ticker_price)
#                     alert.save()  
#                     # Update the cache with the modified queryset
#                     WebSocketConsumer.send_new_alert(alert)
                    
#                 except:
#                     continue
#     ## calculate the total result of strategy ##
#     result_strategy.success += result_success
#     result_strategy.total += result_total
#     result_strategy.save()


# ## ema function ##
# def ema(timespan):
#     # print("getting EMA")
#     tickers = get_cached_queryset()
#     ## initialize results parameters ##
#     result_strategy = Result.objects.get(strategy='EMA',time_frame=timespan)
#     result_success = 0
#     result_total = 0
#     i = 0
#     for ticker in tickers[800:900]:
#         i += 1
#         print(f"EMA {timespan} {i}")
#         result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='ema')
#         if result != []:
#             try:
#                 ema_value = result[0]['ema']
#                 current_price = result[0]['close']
#                 old_price = result[1]['close']
#                 old_ema = result[1]['ema']
#                 older_price = result[2]['close']
#             except BaseException:
#                 continue
#             # to calculate results of strategy success according to current price and the old prices #
#             if (
#                 (old_ema < old_price and old_ema > older_price and current_price < old_price) or 
#                 (old_ema > old_price and old_ema < older_price and current_price > old_price)
#                 ):
#                 result_success += 1
#                 result_total += 1
#             else:
#                 result_total += 1
#             # Creating the Alert object and sending it to the websocket
#             risk_level = None
#             if ema_value < current_price and ema_value > old_price:
#                 risk_level = 'Bullish'
#             if ema_value > current_price and ema_value < old_price:
#                 risk_level = 'Bearish'
#             if risk_level != None:   
#                 try:
#                     caching = alerts_today(key_name=timespan)
#                     print("caching ema",caching)
#                     caching[f'{ticker.symbol}'].append({"strategy":"EMA","value":ema_value,"risk level":risk_level})
#                     cache.set(f"TodayAlerts_{timespan}", caching, timeout=86400)
#                     alert = Alert.objects.create(ticker=ticker , strategy= 'EMA' ,time_frame=timespan ,risk_level=risk_level , result_value = ema_value, current_price=current_price)
#                     alert.save()
#                     # Update the cache with the modified queryset
#                     WebSocketConsumer.send_new_alert(alert)
#                 except:
#                     continue
#     result_strategy.success += result_success
#     result_strategy.total += result_total
#     result_strategy.save()
# ## endpint for RSI 1day ##
# @shared_task(queue='Main')
# def RSI_1day():
#     rsi(timespan='1day')
# ## view for EMA  1day ##
# @shared_task(queue='Main')
# def EMA_DAY():
#     ema(timespan='1day')
# ## method to print caching ##
# @shared_task(queue='Main')
# def print_caching(*args,**kwargs):
#     caching = cache.get("TodayAlerts_1day")
#     print("yes")
#     print(f"caching Before {caching}") 
#     caching.clear()
#     print(f"caching After {caching}")

# @shared_task(queue='Main')
# def tasks_1day():
#     # cache.delete("TodayAlerts_1day")
#     # Run asynchronous code inside a synchronous task
#     tasks = group(
#                 RSI_1day.s(),
#                 EMA_DAY.s(),
#                 # MajorSupport_1day.s(),
#                 # Unusual_Option_Buys.s(),
#                 #upgrade_to_monthly.s(),
#                 )
#     workflow = chord(tasks)(print_caching.s())


a = True
b = True
c = False

if a and b and c :
    print("true")
else:
    print("false")

