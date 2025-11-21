

import re
import pandas as pd
import numpy as np

# Define the input file path
#file_path = r'C:\Users\smits\Downloads\PRNTFILE.RPT 1.txt'  # If the file is not in the current directory, use a full path.
# PArt 1
#file_path = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll\Pay_Details_History_Labour24_25_Part1.txt"
# Part 2
#file_path = r"C:\Users\smits\Downloads\Pay_Details_HistoryFY25_Labour_Part2.txt"


# # Part 1 of Extract
#file_path = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll\Pay_Details_History_Labour22_23_Part1.txt"
#file_path = r"C:\Users\smits\Downloads\Pay_Details_History_Labour22-23_Part1_InclADJ.txt"
#file_path = r"C:\Users\smits\Downloads\Pay_Details_History_Labour22-23_Part1_Excl_ADJ.txt"

# part 2 of Extract
#file_path = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll\Pay_Details_History_Labour22_23_Part2.txt"
file_path = r"C:\Users\smits\Downloads\Pay_Details_History_Labour22-23_Part2_InclADJ.txt"
#file_path = r"C:\Users\smits\Downloads\Pay_Details_History_Labour22-23_Part2_Excl_ADJ.txt"



super_file_path = r"C:\Git\BigBoats\Payroll_23_formatted.xlsx"


# List to collect structured data records.
records = []

# Context variables for the current pay period and employee.
current_period = None    # Current "Period Ending" date (e.g., '01/06/24').
current_employee = None  # Current employee name (from the line containing 'BANK').

# Regex pattern to identify detail lines that begin with a letter code and a word.
# This pattern matches lines such as "N NORMAL ...", "N EXTRA ...", "E 9 ...", "D SACRIFIC ...", etc.
data_line_pattern = re.compile(r'^[A-Za-z]\s+\S+')

super_line_pattern = re.compile(r"^\s*E\s+(9|8|SUPER)\s+(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")

payno_pattern = re.compile(r"\s*\w+\s+\w+\s+(\d{5})\s+Weekly")

# Open the file and parse line by line.
with open(file_path, 'r') as file:
    for line in file:
        raw_line = line.rstrip('\n')  # Strip the newline character (preserving other spacing for Raw Line).

        # Detect a "Period Ending" line, which signifies the start of a new pay period block.
        if raw_line.strip().startswith("Period Ending:"):
            # Extract the date after "Period Ending:" and update the current period.
            parts = raw_line.split("Period Ending:")
            current_period = parts[1].strip() if len(parts) > 1 else None
            # Reset current employee context for the new period.
            current_employee = None
            continue

        # Detect an employee name line (containing "BANK") and update the current employee context.
        if "BANK" in raw_line:
            # Extract the employee name from before the word "BANK".
            current_employee = raw_line.split("BANK")[0].strip()
            continue

        # Only process detail lines if we have both a period and an employee context.
        if current_period and current_employee:
            # If we encounter the end of an employee's section or a new section (avoid capturing beyond intended block).
            if "Employee Other Account" in raw_line or raw_line.strip().startswith("Period Ending:") or "BANK" in raw_line:
                current_employee = None  # End capturing for the current employee.
                continue

            # Check if the line is a payroll detail line (matches our pattern: letter + word).
            stripped_line = raw_line.lstrip()  # Remove leading spaces for pattern matching.
            if data_line_pattern.match(stripped_line):
                # Split the line into tokens (separated by whitespace).
                tokens = stripped_line.split()
                if not tokens:
                    continue  # Skip if the line is empty after stripping (unlikely in our scenario).

                # Merge numeric tokens followed by a '%' into a single token (e.g., "11.0" + "%" -> "11.0%").
                merged_tokens = []
                i = 0
                while i < len(tokens):
                    # If the current token is a number and the next token is a standalone '%', merge them.
                    if i < len(tokens) - 1 and tokens[i].replace('.', '').isdigit() and tokens[i+1] == '%':
                        merged_tokens.append(tokens[i] + '%')
                        i += 2  # Skip the next token as it has been merged.
                    else:
                        merged_tokens.append(tokens[i])
                        i += 1
                tokens = merged_tokens

                # Determine the Code (first token or first two tokens combined, as needed).
                if len(tokens) > 1:
                    # Combine first and second token for codes like "N NORMAL", "E 9", etc.
                    code = f"{tokens[0]} {tokens[1]}"
                else:
                    # In case there's only one token (a rare scenario for detail lines), use it as the code.
                    code = tokens[0]
                # Prepare the list of tokens that come after the code.
                tokens_after_code = tokens[2:] if len(tokens) > 1 else tokens[1:]

                # If no tokens remain after the code (which would be unusual), skip this line.
                if not tokens_after_code:
                    continue

                # Initialise fields for Hours/Value, Rate, and Amount.
                hours_value = ''
                rate = ''
                amount = ''

                # The last token in tokens_after_code should be the Amount (a numeric value, possibly negative).
                last_token = tokens_after_code[-1]
                if re.match(r'^-?\d+(\.\d+)?$', last_token):
                    # If the last token is purely numeric (e.g., "653.94" or "-120.00"), it's the Amount.
                    amount = tokens_after_code.pop(-1)
                else:
                    # If the last token isn't purely numeric (unexpected in a correct report), take it as Amount anyway.
                    amount = tokens_after_code.pop(-1)

                # Check if the new last token is a rate (contains a '/' or ends with '%').
                if tokens_after_code:
                    potential_rate = tokens_after_code[-1]
                    if potential_rate.endswith('%') or '/' in potential_rate:
                        rate = tokens_after_code.pop(-1)

                # After removing Amount (and possibly Rate), check if the remaining last token is numeric for Hours/Value.
                if tokens_after_code:
                    potential_hours = tokens_after_code[-1]
                    if re.match(r'^-?\d+(\.\d+)?$', potential_hours):
                        hours_value = tokens_after_code.pop(-1)

                # The rest of the tokens constitute the Pay Description.
                pay_description = ' '.join(tokens_after_code).strip()

                # Append the extracted data as a record in our list.
                records.append({
                    "Period Ending": current_period,
                    "Employee Name": current_employee,
                    "Pay No.": payno_pattern.search(raw_line).group(1) if payno_pattern.search(raw_line) else '',
                    "Code": code,
                    "Pay Description": pay_description,
                    "Hours/Value": hours_value,
                    "Rate": rate,
                    "Amount": amount,
                    "Raw Line": raw_line
                })




                

# Create a DataFrame from the records for structured output.
df = pd.DataFrame(records, columns=["Period Ending", "Employee Name", "Pay No.", "Code", "Pay Description", "Hours/Value", "Rate", "Amount", "Raw Line"])





print(df.columns)
# Display the resulting table in the console (without the DataFrame index).
print(df.to_string(index=False))

df.to_csv(r"C:\Users\smits\Downloads\Pay_Details_History_labour_23_part2.csv")


# concat Labour25_PayrollTest_part1.csv and abour25_PayrollTest_part2.csv

## Load the CSV files
df1 = pd.read_csv(r"C:\Users\smits\Downloads\Pay_Details_History_labour_23_part1.csv")
df2 = pd.read_csv(r"C:\Users\smits\Downloads\Pay_Details_History_labour_23_part2.csv")
super_df = pd.read_excel(r"C:\Git\BigBoats\Payroll_23_formatted.xlsx")

# Concatenate the dataframes
combined_df = pd.concat([df1, df2], ignore_index=True)
#Remove rows where Code equals 'E 9' (trim whitespace and handle NaN)

combined_df = combined_df[
    (combined_df['Code'].astype(str).str.strip() != 'E 9') &
    (combined_df['Code'].astype(str).str.strip() != 'E 8') &
    (combined_df['Code'].astype(str).str.strip() != 'E CBUS') &
    (combined_df['Code'].astype(str).str.strip() != 'N HRSBNS') &
    (combined_df['Code'].astype(str).str.strip() != 'O HRSBNS') &
    (combined_df['Code'].astype(str).str.strip() != 'W HRSBNS') &
    (combined_df['Code'].astype(str).str.strip() != 'N AL-CASHO') &
     (combined_df["Code"].astype(str).str.strip() != 'A KM10') &
     (combined_df["Code"].astype(str).str.strip() != 'D SACRIFIC')  & 
     (combined_df["Code"].astype(str).str.strip() != 'N PH')

]
combined_df.to_csv('Testwithoutsupermerge.csv')

# create unique key
combined_df['Key'] = combined_df['Employee Name'].astype(str) + combined_df['Period Ending'].astype(str) + combined_df['Code'].astype(str)

#check to see if truly unique 
# Check if all values in the 'Key' column are unique
if combined_df['Key'].is_unique:
    print("All values in the 'Key' column are unique.")
else:
    print("There are duplicate values in the 'Key' column.")
    # Optionally, display the duplicates
    duplicates = combined_df[combined_df.duplicated('Key', keep=False)]
    print("Duplicate entries:")
    print(duplicates)

# drop perfect duplicates 
#combined_df.drop_duplicates(inplace=True)

# Remove super lines


#Concat combined df and super df


combined_df = pd.concat([combined_df, super_df], ignore_index=True)

combined_df.to_csv('Testwithsupermerge.csv')

#Sort dataset

#combined_df['Period Ending'] = pd.to_datetime(combined_df['Period Ending'], format="%d/%m/%y", errors="coerce")


#combined_df['Period Ending'] = combined_df['Period Ending'].dt.date

combined_df = combined_df.sort_values(by=['Employee Name', 'Period Ending'])



# drop perfect duplicates 
#combined_df.drop_duplicates(inplace=True)

# Save the combined dataframe to a new CSV file
combined_df.to_csv("Labour23_PayrollTest_combined.csv", index=False)

print("Files successfully concatenated into Labour23_PayrollTest_combined.csv")
