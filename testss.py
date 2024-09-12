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

import csv

# Path to your CSV file
input_file = 'output.csv'

# Open the input file for reading
with open(input_file, 'r', newline='') as csv_file:
    reader = csv.reader(csv_file)
    
    # Loop through each row in the CSV file
    for row_num, row in enumerate(reader, start=1):
        print(row[4].strip())
        # print(row)

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

