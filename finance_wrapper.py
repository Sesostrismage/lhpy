import datetime
import os
import pandas as pd

from pathlib import Path


class FinanceWrapper:
    def __init__(self, input_folder, target_year):
        self.input_folder = Path(input_folder)

        # Parse all CSV file names in the 'input' folder
        latest_file = None
        latest_date = None

        for file_name in os.listdir(input_folder):
            if file_name.endswith(".csv"):
                try:
                    # Extract the last 10 characters (excluding the extension) and parse as a date
                    date_str = file_name[-14:-4]  # Assuming format is YYYY-MM-DD.csv
                    file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")

                    # Check if the file date is in the target year and is the latest
                    if file_date.year == target_year:
                        if latest_date is None or file_date > latest_date:
                            latest_date = file_date
                            latest_file = file_name
                except ValueError:
                    # Skip files with invalid date formats
                    continue

        self.input_path = self.input_folder / latest_file
        self.data = pd.read_csv(self.input_path, index_col="shortId")

    def get_account_slug_dict(self):
        """
        Get all unique accountSlug values from the data, pair them with their corresponding
        accountName values, and return them as a dictionary.
        """
        account_slugs = self.data["accountSlug"].unique()
        account_names = self.data["accountName"].unique()

        if len(account_slugs) != len(account_names):
            raise ValueError("Mismatch between accountSlug and accountName counts.")

        return dict(zip(account_slugs, account_names))

    def get_account_sums(self, account_slug):
        """
        Get all transactions for a given accountSlug, split between all negative and positive
        transactions, and return them as a dictionary with the keys "debits" and "credits".

        Args:
            account_slug (str): The accountSlug to filter transactions by.
        """
        account_data = self.data[self.data["accountSlug"] == account_slug]

        debits = account_data[account_data["amount"] < 0]["amount"].sum()
        credits = account_data[account_data["amount"] > 0]["amount"].sum()
        difference = credits + debits

        return {"debits": debits, "credits": credits, "difference": difference}
