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
from Alerts.models import Ticker, Industry

def add_symbols_from_csv(csv_file_path):
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            symbol = row['Symbol']
            name = row["Name"]
            cap = float(row["Market Cap"])  # Convert market cap to float
            industry_type = row["Industry"]
            
            # Get or create the Ticker
            ticker, created = Ticker.objects.get_or_create(
                symbol=symbol,
                defaults={'name': name, 'market_cap': cap}
            )
            print("Added", ticker)

            # Get or create the Industry
            industry, created = Industry.objects.get_or_create(type=industry_type)
            print("Added industry:", industry_type)

            # Associate the ticker with the industry (if not already associated)
            if ticker.industry is None:
                ticker.industry = industry
                ticker.save()
                print(f"Associated {ticker.symbol} with industry {industry.type}")
            

# Call the function with the path to your CSV file
add_symbols_from_csv('Alerts/symbols.csv')
