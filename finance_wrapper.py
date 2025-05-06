import pandas as pd

from pathlib import Path


class FinanceWrapper:
    def __init__(self, input_path):
        self.input_path = Path(input_path)

        if self.input_path.exists() and self.input_path.suffix == ".csv":
            self.data = pd.read_csv(self.input_path, index_col="shortId")
        else:
            raise FileNotFoundError(
                f"File {self.input_path} does not exist or is not a CSV."
            )

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

        return {"debits": debits, "credits": credits}
