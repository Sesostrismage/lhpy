import datetime
import os
import pandas as pd

from pathlib import Path


class FinanceWrapper:
    def __init__(self, input_folder, target_year):
        self.input_folder = Path(input_folder)
        self.target_year = target_year

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

        self.latest_date = latest_date
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

    def get_lighthouse_sums(self):
        """
        Go through all transactions for accountSlug "lighthouse". Sum all transactions in groups.
        One for where the description contains "(Lighthouse Membership)" as "Memberships",
        one for where the description contains "(Lighthouse Donation)" as "Donations",
        and then group sum all remaining transactions by the "expenseTags" column.
        If any transactions have not been included as part of the above steps, print the number
        of unprocessed transactions.
        """
        lighthouse_data = self.data[self.data["accountSlug"] == "lighthouse"]

        # Dict to hold info about transactions to be processed separately.
        transactions_to_process = {
            "Memberships": {
                "description": "Lighthouse Membership",
                "amount": 0,
            },
            "Donations": {
                "description": "Lighthouse Donation",
                "amount": 0,
            },
            "Event balance transfers": {
                "description": "Balance Transfer",
                "amount": 0,
            },
            "Stripe fees": {
                "description": "Transaction to Stripe",
                "amount": 0,
            },
        }

        for transaction in transactions_to_process.values():
            # Filter the data for the current transaction type
            filtered_data = lighthouse_data[
                lighthouse_data["description"].str.contains(
                    transaction["description"], na=False
                )
            ]

            # Sum the amounts for the filtered data
            transaction["amount"] = filtered_data["amount"].sum()

        # Remaining transactions grouped by expenseTags
        processed_indices = lighthouse_data[
            lighthouse_data["description"].str.contains(
                "|".join(
                    [
                        transaction["description"]
                        for transaction in transactions_to_process.values()
                    ]
                ),
                na=False,
            )
        ].index

        remaining_data = lighthouse_data[~lighthouse_data.index.isin(processed_indices)]
        grouped_sums = remaining_data.groupby("expenseTags")["amount"].sum().to_dict()

        transactions_to_process["Other Transactions"] = {
            "description": "Other Transactions",
            "sums": grouped_sums,
        }

        # Count unprocessed transactions
        unprocessed_count = remaining_data[remaining_data["expenseTags"].isna()].shape[
            0
        ]
        # Get the description of unprocessed transactions
        unprocessed_descriptions = remaining_data[remaining_data["expenseTags"].isna()][
            "description"
        ].unique()

        if unprocessed_count > 0:
            print(f"Number of unprocessed transactions: {unprocessed_count}")
            print(f"Unprocessed transactions: {unprocessed_descriptions}")

        return transactions_to_process

    def get_lighthouse_sums_str(self):
        """
        Format the lighthouse sums into a string for display.

        Returns:
            str: Formatted string with lighthouse sums.
        """
        lighthouse_sums = self.get_lighthouse_sums()
        result = "Lighthouse sums:\n"

        for key, value in lighthouse_sums.items():
            if "sums" in value:
                result += f"{key}:\n"
                for tag, amount in value["sums"].items():
                    result += f"  {tag}: {round(amount, 2)}\n"
            else:
                result += f"{key}: {round(value['amount'], 2)}\n"

        # Sum all the above amounts to get the total.
        total = sum(
            value["amount"] for value in lighthouse_sums.values() if "sums" not in value
        )
        result += (
            f"\nLighthouse total YTD {self.latest_date.date()}: {round(total, 2)}\n"
        )

        return result


def get_account_sum_str(account_name, account_slug, account_sums):
    """
    Format the account sums into a string for display.

    Args:
        account_name (str): The name of the account.
        account_slug (str): The slug of the account.
        account_sums (dict): The sums for the account.

    Returns:
        str: Formatted string with account details and sums.
    """
    return (
        f"Account: {account_name} ({account_slug})\n"
        f"  Debits: {round(account_sums['debits'], 2)}\n"
        f"  Credits: {round(account_sums['credits'], 2)}\n"
        f"  Difference: {round(account_sums['difference'], 2)}\n"
    )
