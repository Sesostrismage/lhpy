import json
import os
from datetime import datetime

from finance_wrapper import FinanceWrapper

# Load settings.json into a dictionary.
with open("settings.json", "r") as file:
    settings = json.load(file)

print(settings)

# Get the year from settings
target_year = settings.get("year")

# Parse all CSV file names in the 'input' folder
input_folder = "input"
latest_file = None
latest_date = None

for file_name in os.listdir(input_folder):
    if file_name.endswith(".csv"):
        try:
            # Extract the last 10 characters (excluding the extension) and parse as a date
            date_str = file_name[-14:-4]  # Assuming format is YYYY-MM-DD.csv
            file_date = datetime.strptime(date_str, "%Y-%m-%d")

            # Check if the file date is in the target year and is the latest
            if file_date.year == target_year:
                if latest_date is None or file_date > latest_date:
                    latest_date = file_date
                    latest_file = file_name
        except ValueError:
            # Skip files with invalid date formats
            continue

finance_wrapper = FinanceWrapper(os.path.join(input_folder, latest_file))
print(finance_wrapper.data.head())
account_slug_dict = finance_wrapper.get_account_slug_dict()

for account_slug, account_name in account_slug_dict.items():
    print(f"Account: {account_name} ({account_slug})")
    account_sums = finance_wrapper.get_account_sums(account_slug)
    print(f"  Debits: {account_sums['debits']}")
    print(f"  Credits: {account_sums['credits']}")
