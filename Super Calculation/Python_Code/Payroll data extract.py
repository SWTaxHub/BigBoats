
# Txt to CSV for Payroll reports

import re
import pandas as pd
import numpy as np



# File path
text_tx = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll\Pay_Details_History_Labour23-24.txt"

# Read the file
with open(text_tx, "r", encoding="utf-8") as file:
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



name_pattern = re.compile(r"([A-Z\s]+)\s+BANK")
line_pattern = re.compile(r"^\s*([NETB])\s+(\S+)\s+(.+?)\s+([\d\.]*)\s+([\d\.]*)/?[H%W%]?[ ]*([\d\.]*)")
super_line_pattern = re.compile(r"^\s*E\s+(9|8|SUPER)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")
tax_line_pattern = re.compile(r"^\s*T\s+(\S+)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")





for line in lines:
    if period_pattern.search(line):
        period_ending = period_pattern.search(line).group(1)
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
            "Emp Group": ""
        })
        continue

    # if header_pattern.search(line):
    #     code_ = header_pattern.search(line).groups()
    #     continue


    


# In the loop
    if header_pattern.search(line):
        code_, pay_no_value = header_pattern.search(line).groups()
        continue

    # if payno_pattern.search(line):
    #     pay_no_value = payno_pattern.search(line).group(1)
    #     continue

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
            "Emp Group": ""
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
            "Emp Group": ""
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
            "Emp Group": ""
        })

# Convert to DataFrame
df = pd.DataFrame(records, columns=[
    "Period Ending", "Code_", "Full Name", "Pay No.", "Line", "Code",
    "Description", "Hours/ Value", "Pay Rate", "Addition", "Deduction",
    "Contrib", "Total", "Cost Centre", "Emp Group"
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

df["Total"] = np.where(
    ~df["Code"].isin(["NORMTAX", "9"]),
    df["Addition"],
    df["Total"]
)

# Export to Excel
df.to_excel("Payroll_24_formatted.xlsx", index=False)
print("Excel file created: Payroll_24_formatted.xlsx")
