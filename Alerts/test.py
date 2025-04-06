import os
import sys
import csv
from django.core.management import execute_from_command_line
from django.db import models

# Add this to ensure Django settings are loaded
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Streetsuite.settings')

import django
django.setup()

from Alerts.models import Ticker, Industry

def add_symbols_from_csv(csv_file_path):
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            symbol = row['Symbol']
            name = row['Name']
            market_cap = float(row['Market Cap'])  # Convert market cap to float
            industry_type = row['Sector']  # The "Sector" column corresponds to the "Industry" field in your model

            # Get or create the Industry based on the Sector (Industry type)
            industry, created = Industry.objects.get_or_create(type=industry_type)
            if created:
                print(f"Created new industry: {industry.type}")
            else:
                print(f"Industry '{industry.type}' already exists.")

            # Create or update the Ticker
            ticker, created = Ticker.objects.get_or_create(
                symbol=symbol,
                defaults={'name': name, 'market_cap': market_cap, 'industry': industry}
            )

            if created:
                print(f"Created new ticker: {ticker.symbol} ({ticker.name})")
            else:
                print(f"Ticker {ticker.symbol} already exists.")

# Call the function with the path to your CSV file
add_symbols_from_csv('Alerts/output.csv')
