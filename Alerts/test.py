# models.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Streetsuite.settings')

import django

django.setup()

from django.db import models

# views.py or management command
import csv
from Alerts.models import Ticker

def add_symbols_from_csv(csv_file_path):
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            symbol = row['Symbol']
            name = row["name"]
            cap = row["Market Cap"]
            indestry = ["Industry"]
            Ticker.objects.create(ticker_name=symbol)
            print("added", symbol)

# Call the function with the path to your CSV file
add_symbols_from_csv('Alerts/symbols.csv')
