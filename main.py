import json

from finance_wrapper import FinanceWrapper, get_account_sum_str

# Load settings.json into a dictionary.
with open("settings.json", "r") as file:
    settings = json.load(file)

# Get the year from settings
target_year = settings.get("year")

finance_wrapper = FinanceWrapper("input", target_year)
account_slug_dict = finance_wrapper.get_account_slug_dict()
account_slugs_this_year_only = ["lighthouse", "gearboxgear"]

finance_wrapper_last_year = FinanceWrapper("input", target_year - 1)

report_str = ""

for account_slug, account_name in account_slug_dict.items():
    # Skip the lighthouse account, it's handled separately in more detail.
    if account_slug == "lighthouse":
        continue

    account_sums = finance_wrapper.get_account_sums(account_slug)

    # Apart from the account_slugs_this_year_only,
    # check if the account_slug is in the previous year
    # and if so, add the sums to the current year sums.
    if account_slug not in account_slugs_this_year_only:
        previous_year_sums = finance_wrapper_last_year.get_account_sums(account_slug)

        # Add the previous year sums to the current year sums.
        for key in account_sums:
            account_sums[key] += previous_year_sums[key]

    # Print the account sums.
    account_sum_str = get_account_sum_str(account_name, account_slug, account_sums)
    print(account_sum_str)
    report_str += account_sum_str + "\n"

lighthouse_sums = finance_wrapper.get_lighthouse_sums()
lighthouse_sum_str = finance_wrapper.get_lighthouse_sums_str()
print(lighthouse_sum_str)
report_str += lighthouse_sum_str

# Save the lighthouse sum string to the output folder, file name contains the latest date.
output_file_name = (
    f"lighthouse_sums_{finance_wrapper.latest_date.strftime('%Y-%m-%d')}.txt"
)
output_file_path = f"output/{output_file_name}"
with open(output_file_path, "w") as output_file:
    output_file.write(report_str)
