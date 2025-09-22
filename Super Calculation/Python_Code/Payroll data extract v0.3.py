
# Txt to CSV for Payroll reports

import re
import pandas as pd
import numpy as np
from datetime import date


# File path
# Labour File Path
#text_tx = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll\Pay_Details_HistoryFY24_NewExtract.txt"

# Part 1 of Extract
Text_part1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll\Pay_Details_History_Labour22_23_Part1.txt"


# part 2 of Extract
Text_part2 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll\Pay_Details_History_Labour22_23_Part2.txt"

# Offshore File Path
#text_tx = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Payroll\Pay_Details_History_OffSHOREFY24.txt"
# Read the file


def process_payroll_file(filepath):
    # code as provided has been wrapped in a function and cleaned up
    # returns: processed DataFrame and earliest rate changes DataFrame




    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()

    records = []
    period_ending = ""
    header_ = ""
    full_name = ""
    pay_no_value = ""
    code_ = ""

    # Regex patterns
    payno_pattern = re.compile(r"\s*\w+\s+\w+\s+(\d{5})\s+Weekly")
    period_pattern = re.compile(r"Period Ending:\s+(\d{2}/\d{2}/\d{2})")

    #header_pattern = re.compile(r"(\w{4})\s+\w+\s+(\d+)\s+Weekly Pay")

    header_pattern = re.compile(r"^\s*(\w{4})\s+\w+\s+(\d{5})\s+Weekly")

    termination_header_pattern = re.compile(r"^\s*(\w{4})\s+\w+\s+(\d{5})\s+Weekly")

    is_termination = False



    name_pattern = re.compile(r"([A-Z\s]+)\s+BANK")
    #line_pattern = re.compile(r"^\s*([NETB])\s+(\S+)\s+(.+?)\s+([\d\.]*)\s+([\d\.]*)/?[H%W%]?[ ]*([\d\.]*)")
    line_pattern = re.compile(r"^\s*([NETBOACD])\s+(\S+)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)(?:/H)?(?:/W)?(?:\s+([\d\.]+))?")
    super_line_pattern = re.compile(r"^\s*E\s+(9|8|SUPER)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")
    tax_line_pattern = re.compile(r"^\s*T\s+(\S+)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")






    for line in lines:
        if period_pattern.search(line):
            period_ending = period_pattern.search(line).group(1)
            is_termination = False
            records.append({
                "Period Ending": period_ending,
                "Code_": "",
                "Full Name": "",
                "Pay No.": "",
                "Line": "",
                "Code": "",
                "Description": "",
                "Hours/ Value": "",
                "Pay Rate": "",
                "Addition": "",
                "Deduction": "",
                "Contrib": "",
                "Total": "",
                "Cost Centre": "",
                "Emp Group": "",
                "Is Termination": ""
            })
            continue

        # In the loop
        if header_pattern.search(line):
            code_, pay_no_value = header_pattern.search(line).groups()
            continue


        # Detect termination indicators
        if any(term_key in line for term_key in [
            "Termination Pay A:", "Termination Pay B:", "Termination Pay D:",
            "ETP Taxable:", "ETP Tax-free:"
        ]):
            is_termination = True
            continue

    

        if name_pattern.search(line):
            full_name = name_pattern.search(line).group(1).strip()
            continue

        if super_line_pattern.search(line):
            code, desc, hours, rate, contrib = super_line_pattern.search(line).groups()
            records.append({
                "Period Ending": period_ending,
                "Code_": code_,
                "Full Name": full_name,
                "Pay No.": pay_no_value,
                "Line": "E",
                "Code": code,
                "Description": desc.strip(),
                "Hours/ Value": hours,
                "Pay Rate": rate,
                "Addition": "",
                "Deduction": "",
                "Contrib": contrib,
                "Total": "",
                "Cost Centre": "-NO COSTING-",
                "Emp Group": "",
                "Is Termination": is_termination
            })
            continue

        if tax_line_pattern.search(line):
            code, desc, hours, rate, deduction = tax_line_pattern.search(line).groups()
            records.append({
                "Period Ending": period_ending,
                "Code_": code_,
                "Full Name": full_name,
                "Pay No.": pay_no_value,
                "Line": "T",
                "Code": code,
                "Description": desc.strip(),
                "Hours/ Value": hours,
                "Pay Rate": rate,
                "Addition": "",
                "Deduction": deduction,
                "Contrib": "",
                "Total": "",
                "Cost Centre": "-NO COSTING-",
                "Emp Group": "",
                "Is Termination": is_termination
            })
            continue








        if line_pattern.search(line):
            line_code, code, desc, hours, rate, addition = line_pattern.search(line).groups()
            records.append({
                "Period Ending": period_ending,
                "Code_": code_,
                "Full Name": full_name,
                "Pay No.": pay_no_value,
                "Line": line_code,
                "Code": code,
                "Description": desc.strip(),
                "Hours/ Value": hours,
                "Pay Rate": rate,
                "Addition": addition,
                "Deduction": "",
                "Contrib": "",
                "Total": "",
                "Cost Centre": "-NO COSTING-",
                "Emp Group": "",
                "Is Termination": is_termination
            })





    # Convert to DataFrame
    df = pd.DataFrame(records, columns=[
        "Period Ending", "Code_", "Full Name", "Pay No.", "Line", "Code",
        "Description", "Hours/ Value", "Pay Rate", "Addition", "Deduction",
        "Contrib", "Total", "Cost Centre", "Emp Group", "Is Termination"
    ])

    # Data cleaning and type conversion
    df["Pay Rate"] = df["Pay Rate"].replace("", "0").astype(float)
    df["Hours/ Value"] = df["Hours/ Value"].replace("", "0").astype(float)
    df["Contrib"] = df["Contrib"].replace("", "0").astype(float)
    df["Code"] = df["Code"].astype(str).str.strip()

    # Total calculation logic
    df["Total"] = np.where(
        (df["Code"] == "9") & (df["Contrib"] == 0),
        (df["Pay Rate"] / 100) * df["Hours/ Value"],
        np.where(
            (df["Code"] == "9") & (df["Contrib"] != 0),
            df["Contrib"],
            df["Total"]
        )
    )

    df["Total"] = np.where(
        df["Code"] == "NORMTAX",
        (df["Pay Rate"] / 100) * df["Hours/ Value"],
        df["Total"]
    )

    return df



P1 = process_payroll_file(Text_part1)
P2 = process_payroll_file(Text_part2)

#df_with_rates = pd.concat([P2, P1], ignore_index=True).drop_duplicates()



df_with_rates = pd.concat([P2, P1], ignore_index=True)

# Flag duplicates based on the 5 columns
df_with_rates["Is_Duplicate"] = df_with_rates.duplicated(
    subset=["Period Ending", "Code_", "Pay No.", "Line", "Code", 
            'Hours/ Value',	'Pay Rate',	'Addition',	'Deduction', 'Contrib',
            'Total'# 'Pay Rate_Effective'

],
    keep=False  # Marks all duplicates as True (not just the second one)
)



print(df_with_rates.dtypes)

  # Need to create a table for Pay rates for each Code_ by period ending


    # Step 1: Filter for NORMAL code
df_normal = df_with_rates[df_with_rates["Code"] == "NORMAL"].copy()

    # Step 2: Convert 'Period Ending' to datetime if it's not already
df_normal["Period Ending"] = pd.to_datetime(df_normal["Period Ending"], format="%d/%m/%y", errors="coerce")

    # Step 3: Drop duplicates to avoid multiple entries for the same pay rate on the same day
df_unique = df_normal.drop_duplicates(subset=["Code_", "Pay Rate", "Period Ending"])

    # Step 4: Get earliest period for each Code_ and Pay Rate combo
earliest_rate_change = df_unique.groupby(["Code_", "Pay Rate"])["Period Ending"].min().reset_index()

    # Step 5: Optional sort for clarity
earliest_rate_change = earliest_rate_change.sort_values(["Code_", "Period Ending"])


earliest_rate_change['Pay Rate'] = earliest_rate_change['Pay Rate'].astype(float).round(2)

print("Earliest Pay Rate Changes by Code and Period Ending:")
print(earliest_rate_change)
earliest_rate_change.to_excel("Earliest_Pay_Rate_Changes.xlsx", index=False)


    #drop blank rows

columns_to_check = ['Code_', 'Full Name', 'Pay No.', 'Line', 'Code', 'Description']

    # Drop rows where all specified columns are blank or NaN
df_with_rates[columns_to_check] = df_with_rates[columns_to_check].replace(r'^\s*$', np.nan, regex=True)
df_with_rates = df_with_rates.dropna(subset=columns_to_check, how='all')


    # Step 1: Convert to datetime first
df_with_rates["Period Ending"] = pd.to_datetime(df_with_rates["Period Ending"], format="%d/%m/%y", errors="coerce")
earliest_rate_change["Period Ending"] = pd.to_datetime(earliest_rate_change["Period Ending"], format="%d/%m/%y", errors="coerce")

    # Step 2: CORRECT sort order (first Period Ending, then Code_)
df_sorted = df_with_rates.sort_values(by=["Period Ending", "Code_"]).reset_index(drop=True)
earliest_rate_change_sorted = earliest_rate_change.sort_values(by=["Period Ending", "Code_"]).reset_index(drop=True)


# Step 3: Perform merge_asof with correctly sorted data
df_with_rates = pd.merge_asof(
        df_sorted,
        earliest_rate_change_sorted,
        on="Period Ending",
        by="Code_",
        direction="backward",
        suffixes=("", "_Effective")
    )


print("DF with rate columns: ")
print(df_with_rates.columns)

print(df_with_rates.values)

df_with_rates['Hours/ Value'] = df_with_rates["Hours/ Value"].astype(float)
df_with_rates['Pay Rate_Effective'] =  df_with_rates["Pay Rate_Effective"].astype(float)
df_with_rates['Pay Rate'] = df_with_rates['Pay Rate'].astype(float)


    # Step 5: Apply fallback logic to other codes (use df_with_rates not df)
df_with_rates["Total"] = np.where(
        ~df_with_rates["Code"].isin(["NORMTAX", "9"]),
        df_with_rates["Addition"],
        df_with_rates["Total"]
    )



    # Manual intervention for STRG on 1/07/2023

    # Apply the condition using a date object
df_with_rates["Pay Rate_Effective"] = np.where(
        (df_with_rates['Code_'] == 'STRG') & (df_with_rates['Period Ending'].dt.date == date(2023, 7, 1)),
        55.52,
        df_with_rates["Pay Rate_Effective"]
    )
df_with_rates["Period Ending"] = pd.to_datetime(df_with_rates["Period Ending"], format="%d/%m/%y", errors="coerce").dt.date


    # Step 4: Apply updated LOADING totals using the matched pay rate
df_with_rates["Total"] = np.where(
        df_with_rates["Code"] == "LOADING",
        ((df_with_rates["Pay Rate_Effective"] * (df_with_rates['Hours/ Value'])) * (df_with_rates['Pay Rate']/100)),
        df_with_rates["Total"]
    )




df_with_rates['Total'] = df_with_rates['Total'].astype(float)

df_with_rates['Total'] = df_with_rates['Total'].round(2)



def filter_pay_numbers(df):
        filtered_df = df.groupby('Pay No.').filter(lambda group: (group['Line'] == 'B').any())
        return filtered_df






df_filrted = filter_pay_numbers(df_with_rates)







df_filrted.to_excel('Payroll_23_Test.xlsx', index=False)



# Step 6: Export the final dataframe
df_with_rates.to_excel("Payroll_23_formatted.xlsx", index=False)
print("Excel file created: Payroll_23_formatted.xlsx")

