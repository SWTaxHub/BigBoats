
# Txt to CSV for Payroll reports

import re
import pandas as pd
import numpy as np


#text_tx = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\test.txt"\

text_tx = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll\Pay_Details_History_Labour23-24.txt"

# # Read the file
# with open(text_tx, "r", encoding="utf-8") as file:
#     lines = file.readlines()

# # Prepare storage
# records = []
# period_ending = ""
# code_ = ""
# full_name = ""
# pay_no = ""

# # Regex patterns
# period_pattern = re.compile(r"Period Ending:\s+(\d{2}/\d{2}/\d{2})")
# header_pattern = re.compile(r"(\w{4})\s+\w+\s+(\d+)\s+Weekly Pay")
# name_pattern = re.compile(r"([A-Z\s]+)\s+BANK")
# line_pattern = re.compile(r"([NETB])\s+(\w+)\s+(.+?)\s+([\d\.]*)\s*([\d\.]*)/H\s*([\d\.]*)")

# for line in lines:
#     period_match = period_pattern.search(line)
#     if period_match:
#         period_ending = period_match.group(1)
#         continue

#     header_match = header_pattern.search(line)
#     if header_match:
#         code_ = header_match.group(1)
#         pay_no = header_match.group(2)
#         continue

#     name_match = name_pattern.search(line)
#     if name_match:
#         full_name = name_match.group(1).strip()
#         continue

#     line_match = line_pattern.search(line)
#     if line_match:
#         line_code = line_match.group(1)
#         code = line_match.group(2)
#         description = line_match.group(3).strip()
#         hours_value = line_match.group(4)
#         pay_rate = line_match.group(5)
#         total = line_match.group(6)

#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no,
#             "Line": line_code,
#             "Code": code,
#             "Description": description,
#             "Hours/Value": hours_value,
#             "Pay Rate": pay_rate,
#             "Total": total,
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": ""
#         })

# # Convert to DataFrame and save to Excel
# df = pd.DataFrame(records)
# df.to_excel("Payroll_Extract.xlsx", index=False)
# print("Excel file created: Payroll_Extract.xlsx")




# Read the file

# with open(text_tx, "r", encoding="utf-8") as file:
#     lines = file.readlines()


# # Prepare storage
# records = []
# period_ending = ""
# code_ = ""
# full_name = ""
# pay_no = ""

# # Regex patterns
# period_pattern = re.compile(r"Period Ending:\s+(\d{2}/\d{2}/\d{2})")
# header_pattern = re.compile(r"(\w{4})\s+\w+\s+(\d+)\s+Weekly Pay")
# name_pattern = re.compile(r"([A-Z\s]+)\s+BANK")
# line_pattern = re.compile(r"([NETB])\s+(\w+)\s+(.+?)\s+([\d\.]*)\s*([\d\.]*)/H\s*([\d\.]*)")

# for line in lines:
#     period_match = period_pattern.search(line)
#     if period_match:
#         period_ending = period_match.group(1)
#         # Add a blank row for the new period
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": "",
#             "Full Name": "",
#             "Pay No.": "",
#             "Line": "",
#             "Code": "",
#             "Description": "",
#             "Hours/Value": "",
#             "Pay Rate": "",
#             "Total": "",
#             "Cost Centre": "",
#             "Emp Group": ""
#         })
#         continue

#     header_match = header_pattern.search(line)
#     if header_match:
#         code_ = header_match.group(1)
#         pay_no = header_match.group(2)
#         continue

#     name_match = name_pattern.search(line)
#     if name_match:
#         full_name = name_match.group(1).strip()
#         continue

#     line_match = line_pattern.search(line)
#     if line_match:
#         line_code = line_match.group(1)
#         code = line_match.group(2)
#         description = line_match.group(3).strip()
#         hours_value = line_match.group(4)
#         pay_rate = line_match.group(5)
#         total = line_match.group(6)

#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no,
#             "Line": line_code,
#             "Code": code,
#             "Description": description,
#             "Hours/Value": hours_value,
#             "Pay Rate": pay_rate,
#             "Total": total,
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": ""
#         })

# # Convert to DataFrame and save to Excel
# df = pd.DataFrame(records)
# df.to_excel("Payroll_Formatted.xlsx", index=False)
# print("Excel file created: Payroll_Formatted.xlsx")



# import re
# import pandas as pd



# 3:54pm 80725

import re
import pandas as pd

# Read the file

with open(text_tx, "r", encoding="utf-8") as file:
    lines = file.readlines()



records = []
period_ending = ""
code_ = ""
full_name = ""
pay_no = ""

# Regex patterns
period_pattern = re.compile(r"Period Ending:\s+(\d{2}/\d{2}/\d{2})")
header_pattern = re.compile(r"(\w{4})\s+\w+\s+(\d+)\s+Weekly Pay")
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

    if header_pattern.search(line):
        code_, pay_no = header_pattern.search(line).groups()
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
            "Pay No.": pay_no,
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
            "Pay No.": pay_no,
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
            "Pay No.": pay_no,
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

df = pd.DataFrame(records, columns=[
    "Period Ending", "Code_", "Full Name", "Pay No.", "Line", "Code",
    "Description", "Hours/ Value", "Pay Rate", "Addition", "Deduction",
    "Contrib", "Total", "Cost Centre", "Emp Group"
])

df["Pay Rate"]  = df["Pay Rate"].replace("", "0").astype(float)
df["Hours/ Value"] = df["Hours/ Value"].replace("", "0").astype(float)
df['Contrib'] = df['Contrib'].replace("", "0").astype(float)
df['Code'] = df['Code'].astype(str)
df['Code'] = df['Code'].str.strip()


df['Total'] = np.where(
    (df['Code'] == '9') & (df['Contrib'] == 0),
    (df['Pay Rate'] / 100) * df['Hours/ Value'],
    np.where(
        (df['Code'] == '9') & (df['Contrib'] != 0),
        df['Contrib'],
        df['Total']
    )
)


df['Total'] = np.where(df['Code'] == 'NORMTAX', (df['Pay Rate'] / 100) * df['Hours/ Value'], df['Total'])



df['Total'] = np.where(
    ~df['Code'].isin(['NORMTAX', '9']),
    df['Addition'],
    df['Total']
)


df.to_excel("Payroll_24_formatted.xlsx", index=False)
print("Excel file created: Payroll_Formatted.xlsx")


# with open(text_tx, "r", encoding="utf-8") as file:
#     lines = file.readlines()



# records = []
# period_ending = ""
# code_ = ""
# full_name = ""
# pay_no = ""

# # Patterns
# period_pattern = re.compile(r"Period Ending:\s+(\d{2}/\d{2}/\d{2})")
# header_pattern = re.compile(r"(\w{4})\s+\w+\s+(\d+)\s+Weekly Pay")
# name_pattern = re.compile(r"([A-Z\s]+)\s+BANK")
# normal_line_pattern = re.compile(r"([NETB])\s+(\w+)\s+(.+?)\s+([\d\.]*)\s*([\d\.]*)/H\s*([\d\.]*)")
# super_line_pattern = re.compile(r"E\s+(9|8|SUPER)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")
# tax_line_pattern = re.compile(r"T\s+(\w+)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")

# for line in lines:
#     if period_pattern.search(line):
#         period_ending = period_pattern.search(line).group(1)
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": "",
#             "Full Name": "",
#             "Pay No.": "",
#             "Line": "",
#             "Code": "",
#             "Description": "",
#             "Hours/Value": "",
#             "Pay Rate": "",
#             "Total": "",
#             "Cost Centre": "",
#             "Emp Group": ""
#         })
#         continue

#     if header_pattern.search(line):
#         code_, pay_no = header_pattern.search(line).groups()
#         continue

#     if name_pattern.search(line):
#         full_name = name_pattern.search(line).group(1).strip()
#         continue

#     if normal_line_pattern.search(line):
#         line_code, code, desc, hours, rate, total = normal_line_pattern.search(line).groups()
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no,
#             "Line": line_code,
#             "Code": code,
#             "Description": desc.strip(),
#             "Hours/Value": hours,
#             "Pay Rate": rate,
#             "Total": total,
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": ""
#         })
#         continue

#     if super_line_pattern.search(line):
#         code, desc, hours, rate, contrib = super_line_pattern.search(line).groups()
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no,
#             "Line": "E",
#             "Code": code,
#             "Description": desc.strip(),
#             "Hours/Value": hours,
#             "Pay Rate": rate,
#             "Total": contrib,
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": ""
#         })
#         continue

#     if tax_line_pattern.search(line):
#         code, desc, hours, rate, deduction = tax_line_pattern.search(line).groups()
#         records.append({
#             "Period Ending": period_ending,
#             "Code_": code_,
#             "Full Name": full_name,
#             "Pay No.": pay_no,
#             "Line": "T",
#             "Code": code,
#             "Description": desc.strip(),
#             "Hours/Value": hours,
#             "Pay Rate": rate,
#             "Total": deduction,
#             "Cost Centre": "-NO COSTING-",
#             "Emp Group": ""
#         })
#         continue

# df = pd.DataFrame(records)
# df.to_excel("Payroll_Formatted.xlsx", index=False)
# print("Excel file created: Payroll_Formatted.xlsx")










# # Prepare storage
# # records = []
# # period_ending = ""
# # code_ = ""
# # full_name = ""
# # pay_no = ""

# # # Regex patterns
# # period_pattern = re.compile(r"Period Ending:\s+(\d{2}/\d{2}/\d{2})")
# # header_pattern = re.compile(r"(\w{4})\s+\w+\s+(\d+)\s+Weekly Pay")
# # name_pattern = re.compile(r"([A-Z\s]+)\s+BANK")
# # normal_line_pattern = re.compile(r"([NETB])\s+(\w+)\s+(.+?)\s+([\d\.]*)\s*([\d\.]*)/H\s*([\d\.]*)")
# # other_line_pattern = re.compile(r"([TEB])\s+(\w+)\s+(.+?)\s+([\d\.]*)\s*([\d\.]*)\s*([\d\.]*)")

# # for line in lines:
# #     period_match = period_pattern.search(line)
# #     if period_match:
# #         period_ending = period_match.group(1)
# #         # Add a blank row for the new period
# #         records.append({
# #             "Period Ending": period_ending,
# #             "Code_": "",
# #             "Full Name": "",
# #             "Pay No.": "",
# #             "Line": "",
# #             "Code": "",
# #             "Description": "",
# #             "Hours/Value": "",
# #             "Pay Rate": "",
# #             "Total": "",
# #             "Cost Centre": "",
# #             "Emp Group": ""
# #         })
# #         continue

# #     header_match = header_pattern.search(line)
# #     if header_match:
# #         code_ = header_match.group(1)
# #         pay_no = header_match.group(2)
# #         continue
# #     name_match = name_pattern.search(line)
# #     if name_match:
# #         full_name = name_match.group(1).strip()
# #         continue

# #     line_match = normal_line_pattern.search(line)
# #     if line_match:
# #         line_code = line_match.group(1)
# #         code = line_match.group(2)
# #         description = line_match.group(3).strip()
# #         hours_value = line_match.group(4)
# #         pay_rate = line_match.group(5)
# #         total = line_match.group(6)

# #         records.append({
# #             "Period Ending": period_ending,
# #             "Code_": code_,
# #             "Full Name": full_name,
# #             "Pay No.": pay_no,
# #             "Line": line_code,
# #             "Code": code,
# #             "Description": description,
# #             "Hours/Value": hours_value,
# #             "Pay Rate": pay_rate,
# #             "Total": total,
# #             "Cost Centre": "-NO COSTING-",
# #             "Emp Group": ""
# #         })
# #         continue

# #     line_match = other_line_pattern.search(line)
# #     if line_match:
# #         line_code = line_match.group(1)
# #         code = line_match.group(2)
# #         description = line_match.group(3).strip()
# #         hours_value = line_match.group(4)
# #         pay_rate = line_match.group(5)
# #         total = line_match.group(6)

# #         records.append({
# #             "Period Ending": period_ending,
# #             "Code_": code_,
# #             "Full Name": full_name,
# #             "Pay No.": pay_no,
# #             "Line": line_code,
# #             "Code": code,
# #             "Description": description,
# #             "Hours/Value": hours_value,
# #             "Pay Rate": pay_rate,
# #             "Total": total,
# #             "Cost Centre": "-NO COSTING-",
# #             "Emp Group": ""
# #         })

# # # Convert to DataFrame and save to Excel
# # df = pd.DataFrame(records)
# # df.to_excel("Payroll_Formatted.xlsx", index=False)
# # print("Excel file created: Payroll_Formatted.xlsx")
