
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
full_name = ""
pay_no_value = ""
code_ = ""

# Target codes to filter
target_codes = [
    "AL", "AL-CASHO", "BACK", "BEREAVE", "BONUS", "BPAY", "CASBNS", "EXTRA", "FLEXI",
    "HRSBNS", "LOAD", "LOADING", "LSL", "NORMAL", "ORD", "OT1.5", "OT2.0", "OT2.5",
    "PH", "PL-VACC", "SL", "TAFE", "WCOMP-EX", "WCOMP", "WRKDJ"
]

# Regex patterns
period_pattern = re.compile(r"Period Ending:\s+(\d{2}/\d{2}/\d{2})")
header_pattern = re.compile(r"^\s*(\w{4})\s+\w+\s+(\d{5})\s+Weekly")
name_pattern = re.compile(r"([A-Z\s]+)\s+BANK")
super_line_pattern = re.compile(r"^\s*E\s+(9|8|SUPER)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")
tax_line_pattern = re.compile(r"^\s*T\s+(\S+)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")

standard_line_pattern = re.compile(r"^\s*([NETB])\s+(\S+)\s+(.+?)\s+([\d\.]+)?\s+([\d\.]+)?(?:/?[H%W])?\s*([\d\.]+)?")
loading_pattern = re.compile(r"^\s*A\s+LOADING\s+ANNUAL\s+LEAVE\s+LOADING\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")
dated_code_pattern = re.compile(r"^\s*N\s+(PH|SL|AL)\s+(\d{2}/\d{2}/\d{2})\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)")
bonus_pattern = re.compile(r"^\s*N\s+(CASBNS|HRSBNS)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)")
backpay_pattern = re.compile(r"^\s*O\s+(BPAY|BONUS|BACK)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")

is_termination = False

for line in lines:
    if period_pattern.search(line):
        period_ending = period_pattern.search(line).group(1)
        is_termination = False
        continue

    if header_pattern.search(line):
        code_, pay_no_value = header_pattern.search(line).groups()
        continue

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
        if code in target_codes:
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
        if code in target_codes:
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

    matched = False
    addition = ""

    for pattern, line_type in [
        (loading_pattern, "A"),
        (dated_code_pattern, "N"),
        (bonus_pattern, "N"),
        (backpay_pattern, "O"),
        (standard_line_pattern, None)
    ]:
        match = pattern.search(line)
        if match:
            matched = True
            if pattern == loading_pattern:
                hours, rate, addition = match.groups()
                code = "LOADING"
                desc = "ANNUAL LEAVE LOADING"
            elif pattern == dated_code_pattern:
                code, date, desc, hours, rate = match.groups()
                desc = f"{desc.strip()} ({date})"
            elif pattern == bonus_pattern:
                code, desc, hours, rate = match.groups()
            elif pattern == backpay_pattern:
                code, hours, rate, addition = match.groups()
                desc = "Backpay or Bonus"
            elif pattern == standard_line_pattern:
                line_code, code, desc, hours, rate, addition = match.groups()
                line_type = line_code

            if code in target_codes:
                records.append({
                    "Period Ending": period_ending,
                    "Code_": code_,
                    "Full Name": full_name,
                    "Pay No.": pay_no_value,
                    "Line": line_type or "N",
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
            break

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

df["Total"] = np.where(
    ~df["Code"].isin(["NORMTAX", "9"]),
    df["Addition"],
    df["Total"]
)

# Export to Excel
df.to_excel("Payroll_24_formatted.xlsx", index=False)
print("Excel file created: Payroll_24_formatted.xlsx")























###### OLD COLD ########################

# # File path
# text_tx = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll\Pay_Details_History_Labour23-24.txt"

# # Read the file
# with open(text_tx, "r", encoding="utf-8") as file:
#     lines = file.readlines()

# records = []
# period_ending = ""
# header_ = ""
# full_name = ""
# pay_no_value = ""
# code_ = ""

# # Regex patterns
# payno_pattern = re.compile(r"\s*\w+\s+\w+\s+(\d{5})\s+Weekly")
# period_pattern = re.compile(r"Period Ending:\s+(\d{2}/\d{2}/\d{2})")

# #header_pattern = re.compile(r"(\w{4})\s+\w+\s+(\d+)\s+Weekly Pay")

# header_pattern = re.compile(r"^\s*(\w{4})\s+\w+\s+(\d{5})\s+Weekly")

# termination_header_pattern = re.compile(r"^\s*(\w{4})\s+\w+\s+(\d{5})\s+Weekly")

# is_termination = False



# name_pattern = re.compile(r"([A-Z\s]+)\s+BANK")
# line_pattern = re.compile(r"^\s*([NETB])\s+(\S+)\s+(.+?)\s+([\d\.]*)\s+([\d\.]*)/?[H%W%]?[ ]*([\d\.]*)")
# super_line_pattern = re.compile(r"^\s*E\s+(9|8|SUPER)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")
# tax_line_pattern = re.compile(r"^\s*T\s+(\S+)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")


# standard_line_pattern = re.compile(
#     r"^\s*([NETB])\s+(\S+)\s+(.+?)\s+([\d\.]+)?\s+([\d\.]+)?(?:/?[H%W])?\s*([\d\.]+)?"
# )

# loading_pattern = re.compile(
#     r"^\s*A\s+LOADING\s+ANNUAL\s+LEAVE\s+LOADING\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)"
# )


# dated_code_pattern = re.compile(
#     r"^\s*N\s+(PH|SL|AL)\s+(\d{2}/\d{2}/\d{2})\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)"
# )

# bonus_pattern = re.compile(
#     r"^\s*N\s+(CASBNS|HRSBNS)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)"
# )

# backpay_pattern = re.compile(
#     r"^\s*O\s+(BPAY|BONUS|BACK)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)"
# )






# for line in lines:
#     if period_pattern.search(line):
#         period_ending = period_pattern.search(line).group(1)
#         is_termination = False
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": "",
#             "Full Name": "",
#             "Pay No.": "",
#             "Line": "",
#             "Code": "",
#             "Description": "",
#             "Hours/ Value": "",
#             "Pay Rate": "",
#             "Addition": "",
#             "Deduction": "",
#             "Contrib": "",
#             "Total": "",
#             "Cost Centre": "",
#             "Emp Group": "",
#             "Is Termination": ""
#         })
#         continue

#     # In the loop
#     if header_pattern.search(line):
#         code_, pay_no_value = header_pattern.search(line).groups()
#         continue


#      # Detect termination indicators
#     if any(term_key in line for term_key in [
#         "Termination Pay A:", "Termination Pay B:", "Termination Pay D:",
#         "ETP Taxable:", "ETP Tax-free:"
#     ]):
#         is_termination = True
#         continue

  

#     if name_pattern.search(line):
#         full_name = name_pattern.search(line).group(1).strip()
#         continue

#     if super_line_pattern.search(line):
#         code, desc, hours, rate, contrib = super_line_pattern.search(line).groups()
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no_value,
#             "Line": "E",
#             "Code": code,
#             "Description": desc.strip(),
#             "Hours/ Value": hours,
#             "Pay Rate": rate,
#             "Addition": "",
#             "Deduction": "",
#             "Contrib": contrib,
#             "Total": "",
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": "",
#             "Is Termination": is_termination
#         })
#         continue

#     if tax_line_pattern.search(line):
#         code, desc, hours, rate, deduction = tax_line_pattern.search(line).groups()
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no_value,
#             "Line": "T",
#             "Code": code,
#             "Description": desc.strip(),
#             "Hours/ Value": hours,
#             "Pay Rate": rate,
#             "Addition": "",
#             "Deduction": deduction,
#             "Contrib": "",
#             "Total": "",
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": "",
#             "Is Termination": is_termination
#         })
#         continue


#     target_codes = [
#     "AL", "AL-CASHO", "BACK", "BEREAVE", "BONUS", "BPAY", "CASBNS", "EXTRA", "FLEXI",
#     "HRSBNS", "LOAD", "LOADING", "LSL", "NORMAL", "ORD", "OT1.5", "OT2.0", "OT2.5",
#     "PH", "PL-VACC", "SL", "TAFE", "WCOMP-EX", "WCOMP", "WRKDJ"
# ]



#         # Match standard pay lines (N, E, T, B)
#     if standard_line_pattern.search(line):
#         line_code, code, desc, hours, rate, addition = standard_line_pattern.search(line).groups()
#         if code in target_codes:
#             records.append({
#                 "Period Ending": period_ending,
#                 "Code_": code_,
#                 "Full Name": full_name,
#                 "Pay No.": pay_no_value,
#                 "Line": line_code,
#                 "Code": code,
#                 "Description": desc.strip(),
#                 "Hours/ Value": hours,
#                 "Pay Rate": rate,
#                 "Addition": addition,
#                 "Deduction": "",
#                 "Contrib": "",
#                 "Total": "",
#                 "Cost Centre": "-NO COSTING-",
#                 "Emp Group": "",
#                 "Is Termination": is_termination
#             })
#         continue

#     # Match annual leave loading
#     if loading_pattern.search(line):
#         hours, rate, addition = loading_pattern.search(line).groups()
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no_value,
#             "Line": "A",
#             "Code": "LOADING",
#             "Description": "ANNUAL LEAVE LOADING",
#             "Hours/ Value": hours,
#             "Pay Rate": rate,
#             "Addition": addition,
#             "Deduction": "",
#             "Contrib": "",
#             "Total": "",
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": "",
#             "Is Termination": is_termination
#         })
#         continue

#     # Match dated codes like PH, SL, AL
#     if dated_code_pattern.search(line):
#         code, date, desc, hours, rate = dated_code_pattern.search(line).groups()
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no_value,
#             "Line": "N",
#             "Code": code,
#             "Description": f"{desc.strip()} ({date})",
#             "Hours/ Value": hours,
#             "Pay Rate": rate,
#             "Addition": "",
#             "Deduction": "",
#             "Contrib": "",
#             "Total": "",
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": "",
#             "Is Termination": is_termination
#         })
#         continue

#     # Match casual and hourly bonuses
#     if bonus_pattern.search(line):
#         code, desc, hours, rate = bonus_pattern.search(line).groups()
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no_value,
#             "Line": "N",
#             "Code": code,
#             "Description": desc.strip(),
#             "Hours/ Value": hours,
#             "Pay Rate": rate,
#             "Addition": "",
#             "Deduction": "",
#             "Contrib": "",
#             "Total": "",
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": "",
#             "Is Termination": is_termination
#         })
#         continue

#     # Match backpay and one-off payments
#     if backpay_pattern.search(line):
#         code, hours, rate, addition = backpay_pattern.search(line).groups()
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no_value,
#             "Line": "O",
#             "Code": code,
#             "Description": "Backpay or Bonus",
#             "Hours/ Value": hours,
#             "Pay Rate": rate,
#             "Addition": addition,
#             "Deduction": "",
#             "Contrib": "",
#             "Total": "",
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": "",
#             "Is Termination": is_termination
#         })
#         continue







#     # if line_pattern.search(line):
#     #     line_code, code, desc, hours, rate, addition = line_pattern.search(line).groups()
#     #     records.append({
#     #         "Period Ending": period_ending,
#     #         "Code_": code_,
#     #         "Full Name": full_name,
#     #         "Pay No.": pay_no_value,
#     #         "Line": line_code,
#     #         "Code": code,
#     #         "Description": desc.strip(),
#     #         "Hours/ Value": hours,
#     #         "Pay Rate": rate,
#     #         "Addition": addition,
#     #         "Deduction": "",
#     #         "Contrib": "",
#     #         "Total": "",
#     #         "Cost Centre": "-NO COSTING-",
#     #         "Emp Group": "",
#     #         "Is Termination": is_termination
#     #     })




#         # Try expanded patterns first
#     matched = False

#     for pattern, line_type in [
#         (loading_pattern, "A"),
#         (dated_code_pattern, "N"),
#         (bonus_pattern, "N"),
#         (backpay_pattern, "O"),
#         (standard_line_pattern, None)
#     ]:
#         match = pattern.search(line)
#         if match:
#             matched = True
#             if pattern == loading_pattern:
#                 hours, rate, addition = match.groups()
#                 code = "LOADING"
#                 desc = "ANNUAL LEAVE LOADING"
#             elif pattern == dated_code_pattern:
#                 code, date, desc, hours, rate = match.groups()
#                 desc = f"{desc.strip()} ({date})"
#             elif pattern == bonus_pattern:
#                 code, desc, hours, rate = match.groups()
#             elif pattern == backpay_pattern:
#                 code, hours, rate, addition = match.groups()
#                 desc = "Backpay or Bonus"
#             elif pattern == standard_line_pattern:
#                 line_code, code, desc, hours, rate, addition = match.groups()
#                 line_type = line_code

#             records.append({
#                 "Period Ending": period_ending,
#                 "Code_": code_,
#                 "Full Name": full_name,
#                 "Pay No.": pay_no_value,
#                 "Line": line_type or "N",
#                 "Code": code,
#                 "Description": desc.strip(),
#                 "Hours/ Value": hours,
#                 "Pay Rate": rate,
#                 "Addition": addition if 'addition' in locals() else "",
#                 "Deduction": "",
#                 "Contrib": "",
#                 "Total": "",
#                 "Cost Centre": "-NO COSTING-",
#                 "Emp Group": "",
#                 "Is Termination": is_termination
#             })
#             break

#     # Fallback to original line_pattern if nothing matched
#     if not matched and line_pattern.search(line):
#         line_code, code, desc, hours, rate, addition = line_pattern.search(line).groups()
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no_value,
#             "Line": line_code,
#             "Code": code,
#             "Description": desc.strip(),
#             "Hours/ Value": hours,
#             "Pay Rate": rate,
#             "Addition": addition,
#             "Deduction": "",
#             "Contrib": "",
#             "Total": "",
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": "",
#             "Is Termination": is_termination
#         })


# # Convert to DataFrame
# df = pd.DataFrame(records, columns=[
#     "Period Ending", "Code_", "Full Name", "Pay No.", "Line", "Code",
#     "Description", "Hours/ Value", "Pay Rate", "Addition", "Deduction",
#     "Contrib", "Total", "Cost Centre", "Emp Group", "Is Termination"
# ])

# # Data cleaning and type conversion
# df["Pay Rate"] = df["Pay Rate"].replace("", "0").astype(float)
# df["Hours/ Value"] = df["Hours/ Value"].replace("", "0").astype(float)
# df["Contrib"] = df["Contrib"].replace("", "0").astype(float)
# df["Code"] = df["Code"].astype(str).str.strip()

# # Total calculation logic
# df["Total"] = np.where(
#     (df["Code"] == "9") & (df["Contrib"] == 0),
#     (df["Pay Rate"] / 100) * df["Hours/ Value"],
#     np.where(
#         (df["Code"] == "9") & (df["Contrib"] != 0),
#         df["Contrib"],
#         df["Total"]
#     )
# )

# df["Total"] = np.where(
#     df["Code"] == "NORMTAX",
#     (df["Pay Rate"] / 100) * df["Hours/ Value"],
#     df["Total"]
# )

# df["Total"] = np.where(
#     ~df["Code"].isin(["NORMTAX", "9"]),
#     df["Addition"],
#     df["Total"]
# )

# # Export to Excel
# df.to_excel("Payroll_24_formatted.xlsx", index=False)
# print("Excel file created: Payroll_24_formatted.xlsx")
