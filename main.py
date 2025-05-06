import json

from finance_wrapper import FinanceWrapper

# Load settings.json into a dictionary.
with open("settings.json", "r") as file:
    settings = json.load(file)

# Get the year from settings
target_year = settings.get("year")

finance_wrapper = FinanceWrapper("input", target_year)
account_slug_dict = finance_wrapper.get_account_slug_dict()
account_slugs_this_year_only = ["lighthouse", "gearboxgear"]

finance_wrapper_last_year = FinanceWrapper("input", target_year - 1)

for account_slug, account_name in account_slug_dict.items():
    print(f"Account: {account_name} ({account_slug})")
    account_sums = finance_wrapper.get_account_sums(account_slug)

    # Apart from the account_slugs_this_year_only,
    # check if the account_slug is in the previous year
    # and if so, add the sums to the current year sums.
    if account_slug not in account_slugs_this_year_only:
        previous_year_sums = finance_wrapper_last_year.get_account_sums(account_slug)
        account_sums["debits"] += previous_year_sums["debits"]
        account_sums["credits"] += previous_year_sums["credits"]
        account_sums["difference"] += previous_year_sums["difference"]

    print(f"  Debits: {round(account_sums['debits'], 2)}")
    print(f"  Credits: {round(account_sums['credits'], 2)}")
    print(f"  Difference: {round(account_sums['difference'], 2)}\n")
