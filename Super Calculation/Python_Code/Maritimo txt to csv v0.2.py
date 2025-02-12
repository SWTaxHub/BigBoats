import csv
import re

# # file paths for LABOUR employee labels
input_file = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Employee details\Employee_Labels.txt"
output_file = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Employee details\Employee_Labels.csv"

# File paths for Offshore employee Labels
input_file_offshore = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Employee details\Employee_Labels.txt"
output_file_offshore = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Employee details\Employee_Labels.csv"


allowance_details = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Paycode Attributes\Allowance_Details_Report.txt"
allowance_details_output = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Paycode Attributes\Allowance_Details_Report.csv"
# Allowance Details Report

import re
import csv


import re
import csv

def extract_pay_details(input_file, output_file):
    """
    Extracts pay details from a structured text file and writes them into a CSV file.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to save the extracted CSV file.
    """
    # Regex pattern to capture Pay Code & Description
    pay_code_pattern = re.compile(r"^(?P<Pay_Code>\w+)\s+(?P<Description>[\w\s$.,%-]+)\t+(?P<Tax_Treatment>Before|After)\s+(?P<Tax_Cert_Totals>[\w\s]+)")

    # Regex pattern to capture Type & Calculation details
    calculation_pattern = re.compile(r"Type:\s+(?P<Type>[\w\s\(\)]+)\s+.*?Value\s*=\s*(?P<Value>[\d.]+)?\s*(?P<Unit>[A-Za-z/]+)?")

    # Regex pattern to capture Min/Max values
    min_max_pattern = re.compile(r"Min\s+\$\s*=\s*(?P<Min_Value>[\d,.]+).*?Max\s+\$\s*(?P<Max_Value>[\d,.]+)")

    # Regex pattern to capture flags (Yes/No settings)
    flags_pattern = re.compile(r"Show rate on Pay Advice\s*:\s*(?P<Show_Rate>[Yes|No]+).*?Show YTD on Pay Advice\s*:\s*(?P<Show_YTD>[Yes|No]+).*?"
                               r"Allow date entry\s*:\s*(?P<Allow_Date>[Yes|No]+).*?Multiple G/L Dissections\s*:\s*(?P<Multiple_GL>[Yes|No]+).*?"
                               r"Include in SG Threshold\s*:\s*(?P<SG_Threshold>[Yes|No]+).*?Back Pay\s*:\s*(?P<Back_Pay>[Yes|No]+)")

    # Read file content
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Data storage
    extracted_data = []
    current_record = {}

    # Process each line
    for line in lines:
        line = line.strip()

        # Match Pay Code & Description
        match = pay_code_pattern.match(line)
        if match:
            # Save previous record before starting a new one
            if current_record:
                extracted_data.append(current_record)
            # Start new record
            current_record = match.groupdict()
            continue

        # Match Calculation Type & Value
        match = calculation_pattern.search(line)
        if match and current_record:
            current_record.update(match.groupdict())

        # Match Min/Max Values
        match = min_max_pattern.search(line)
        if match and current_record:
            current_record.update(match.groupdict())

        # Match Yes/No settings
        match = flags_pattern.search(line)
        if match and current_record:
            current_record.update(match.groupdict())

    # Append last record
    if current_record:
        extracted_data.append(current_record)

    # Define headers
    headers = ["Pay_Code", "Description", "Tax_Treatment", "Tax_Cert_Totals", "Type", "Value", "Unit", "Min_Value",
               "Max_Value", "Show_Rate", "Show_YTD", "Allow_Date", "Multiple_GL", "SG_Threshold", "Back_Pay"]

    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(extracted_data)

    print(f"✅ CSV file has been saved as {output_file}")

# Example Usage
input_path = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Paycode Attributes\Allowance_Details_Report.txt"
output_path = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Paycode Attributes\Allowance_Details_Reportv0.2.csv"

import re
import csv

def extract_allowance_details(input_file, output_file):
    """
    Extracts pay details from a structured text file and writes them into a CSV file.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to save the extracted CSV file.
    """
    # Regex pattern to capture Pay Code & Description
    pay_code_pattern = re.compile(r"^(?P<Pay_Code>\w+)\s+(?P<Description>[\w\s$.,%-]+)\t+(?P<Tax_Treatment>Before|After)\s+(?P<Tax_Cert_Totals>[\w\s]+)")

    # Regex pattern to capture Type & Calculation details
    calculation_pattern = re.compile(r"Type:\s+(?P<Type>[\w\s\(\)]+)\s+.*?Value\s*=\s*(?P<Value>[\d.]+)?\s*(?P<Unit>[A-Za-z/]+)?")

    # Regex pattern to capture Min/Max values
    min_max_pattern = re.compile(r"Min\s+\$\s*=\s*(?P<Min_Value>[\d,.]+).*?Max\s+\$\s*(?P<Max_Value>[\d,.]+)")

    # Regex pattern to capture flags (Yes/No settings)
    flags_pattern = re.compile(r"Show rate on Pay Advice\s*:\s*(?P<Show_Rate>[Yes|No]+).*?Show YTD on Pay Advice\s*:\s*(?P<Show_YTD>[Yes|No]+).*?"
                               r"Allow date entry\s*:\s*(?P<Allow_Date>[Yes|No]+).*?Multiple G/L Dissections\s*:\s*(?P<Multiple_GL>[Yes|No]+).*?"
                               r"Include in SG Threshold\s*:\s*(?P<SG_Threshold>[Yes|No]+).*?Back Pay\s*:\s*(?P<Back_Pay>[Yes|No]+)")

    # Read file content
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Data storage
    extracted_data = []
    current_record = {}

    # Process each line
    for line in lines:
        line = line.strip()

        # Match Pay Code & Description
        match = pay_code_pattern.match(line)
        if match:
            # Save previous record before starting a new one
            if current_record:
                extracted_data.append(current_record)
            # Start new record
            current_record = match.groupdict()
            continue

        # Match Calculation Type & Value
        match = calculation_pattern.search(line)
        if match and current_record:
            current_record.update(match.groupdict())

        # Match Min/Max Values
        match = min_max_pattern.search(line)
        if match and current_record:
            current_record.update(match.groupdict())

        # Match Yes/No settings
        match = flags_pattern.search(line)
        if match and current_record:
            current_record.update(match.groupdict())

    # Append last record
    if current_record:
        extracted_data.append(current_record)

    # Define headers
    headers = ["Pay_Code", "Description", "Tax_Treatment", "Tax_Cert_Totals", "Type", "Value", "Unit", "Min_Value",
               "Max_Value", "Show_Rate", "Show_YTD", "Allow_Date", "Multiple_GL", "SG_Threshold", "Back_Pay"]

    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(extracted_data)

    print(f"✅ CSV file has been saved as {output_file}")


extract_allowance_details(input_path, output_path)









def convert_allowance_details_to_csv(input_file, output_file):
    """
    Reads a text file containing employee details, extracts relevant information using regex, 
    and writes the data to a CSV file.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output CSV file.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]  # Remove empty lines

    # Updated regex pattern to handle spaces or tabs
    pattern = re.compile(r"^(?P<Code>\S+)\s+(?P<Description>\S+)\s+(?P<TaxStatus>\S+)\s+(?P<TaxCertStatus>.+?)\s+(?P<Inactive>\S+)$")

    data = []
    headers = ["Code", "Description", "Tax Status", "Tax Cert. Status", "Inactive"]

    for line in lines:
        match = pattern.match(line)
        if match:
            data.append(match.groups())
        else:
            print(f"Skipping line (no match): {line}")  # Debugging output

    if not data:
        print("No data extracted. Check the file format or regex pattern.")

    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"CSV file has been saved as {output_file}")

# Call function
convert_allowance_details_to_csv(allowance_details, allowance_details_output)











def convert_employee_labels_to_csv(input_file, output_file):
    """
    Reads a text file containing employee details, extracts relevant information using regex, 
    and writes the data to a CSV file.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output CSV file.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Define a regex pattern to extract key details
    pattern = re.compile(r"Emp\.Code:(\S+)\s+PayPoint:(\S+)\s+(.+?)\s+(\d+.+?)\s+([A-Z]+\s+\d{4} Australia)\s+(.+?)\s+([\w\s\d-]*)")

    data = []
    headers = ["Emp.Code", "PayPoint", "Name", "Address", "City & Postal Code", "Job Role / Department", "Award"]

    for line in lines:
        match = pattern.search(line)
        if match:
            data.append(match.groups())

    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"CSV file has been saved as {output_file}")

convert_employee_labels_to_csv(input_file, output_file)
convert_employee_labels_to_csv(input_file_offshore, output_file_offshore)


#Employee Leave File paths 

# File paths
input_file_empLeave = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.txt"
output_file_empLeave= r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.csv"

# Regular expression to capture employee information (Loc, Employee Name, Leave Start Date, etc.)
employee_info_pattern = re.compile(r'''
    (?P<Location>\w{4})\s+                      # Location (e.g., ALDD)
    (?P<Employee_Name>[\w\s]+?)\s+               # Employee Name
    (?P<Leave_Type>Leave\s+Start\s+Date:)\s+     # Leave Type
    (?P<Leave_Start_Date>\d{2}/\d{2}/\d{2})\s+  # Leave Start Date (e.g., 09/05/08)
    (?P<Hours_Per_Day_Label>Hours\s+per\s+Day:)\s+
    (?P<Hours_Per_Day>\d+\.\d{2})\s*             # Hours per Day (e.g., 7.60)
''', re.VERBOSE)

# Regular expression to capture the detailed rows (Hours, Entitled, Pro Rata, etc.)
detail_info_pattern = re.compile(r'''
    (?P<Detail_Type>\w+)\s+                 # Detail Type (Accrual, Opening Balance, etc.)
    (?P<Entitled_Owing>\d+\.\d{4})\s+      # Entitled Owing (e.g., 0.0000)
    (?P<Pro_Rata_Owing>\d+\.\d{4})\s+      # Pro Rata Owing (e.g., 0.0000)
    (?P<Contingent_Owing>\d+\.\d{4})\s+    # Contingent Owing (e.g., 0.0000)
    (?P<Leave_Code>Hours|Sick|Annual)\s+   # Leave Code (e.g., Hours)
    (?P<Operator>\w+)\s+                   # Operator (e.g., MELISSA)
    (?P<Years>\d+\.\d{2})                  # Years (e.g., 13.77)
''', re.VERBOSE)

# Read the file content
with open(input_file_empLeave, "r", encoding="utf-8") as file:
    content = file.read()

# Split the content into blocks for each employee (assuming each block starts with Location and Employee Name)
blocks = re.split(r'(?=\w{4}\s+[\w\s]+?\s+Leave\s+Start\s+Date:)', content)

# Extract the data from each block
extracted_data = []
for block in blocks:
    # Extract the first line (employee info)
    employee_match = employee_info_pattern.search(block)
    if employee_match:
        employee_info = {
            'Loc': employee_match.group('Location'),
            'Employee Name': employee_match.group('Employee_Name'),
            'Leave Start Date': employee_match.group('Leave_Start_Date'),
            'Hours per Day': employee_match.group('Hours_Per_Day'),
        }

        # Now, extract the detailed rows (Accruals, Entitlements, etc.)
        detail_matches = detail_info_pattern.findall(block)
        for detail in detail_matches:
            data_row = employee_info.copy()  # Copy the employee info to each row
            data_row.update({
                'Entitled Owing': detail[1],
                'Pro Rata Owing': detail[2],
                'Contingent Owing': detail[3],
                'Leave Code': detail[4],
                'Operator': detail[5],
                'Years': detail[6]
            })
            extracted_data.append(data_row)

# Define the CSV headers
headers = ['Loc', 'Employee Name', 'Leave Start Date', 'Hours per Day', 'Entitled Owing', 'Pro Rata Owing', 'Contingent Owing', 'Leave Code', 'Operator', 'Years']

# Write to CSV
with open(output_file_empLeave, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()  # Write headers first
    writer.writerows(extracted_data)  # Write all rows of data

print(f"CSV file has been saved as {output_file_empLeave}")




# Super Text Files 



# File paths for Super 2022 - 2024 LABOUR files
input_file_super22 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 22.txt"
output_file_super22 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 22.csv"


input_file_super23 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 23.txt"
output_file_super23 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 23.csv"


input_file_super24 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 24.txt"
output_file_super24 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 24.csv"




# File paths for Super 2022 - 2024 Offshore files
input_file_super22_offshore = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Super\Superannuation 22.txt"
output_file_super22_offshore =  r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Super\Superannuation 22.csv"

input_file_super23_offshore = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Super\Superannuation 23.txt"
output_file_super23_offshore = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Super\Superannuation 23.csv"

input_file_super24_offshore = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Super\Superannuation 24.txt"
output_file_super24_offshore = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Super\Superannuation 24.csv"


def process_super_data(input_file, output_file):
    headers = ['Loc', 'Emp.Code', 'Employee Name', 'Date Paid', 'Hours Worked', 'Ctrb Type',
               'Supr Pcnt', 'Account Code', 'Threshold Income', 'Monthly Threshold',
               'Min Hours', 'Income for Month', 'Super for Month', 'Income for Pay', 'Super for Pay']
    
    # Read the file
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    # Initialize variables
    current_loc = None
    extracted_data = []
    current_employee = None
    
    # Regex patterns
    loc_pattern = re.compile(r'^\s*(?P<Loc>\d+)\s+')
    employee_info_pattern = re.compile(r'^\s*(?P<Emp_Code>\w+)\s+(?P<Employee_Name>[A-Za-z\s\-]+)')
    detail_info_pattern = re.compile(r'''
        (?P<Date_Paid>\d{2}/\d{2}/\d{2})\s+    
        (?P<Hours_Worked>\d+\.\d{2})\s+        
        (?P<Contribution_Type>[A-Z]+)\s+       
        (?P<Super_Percent>\d+\.\d{2})\s+       
        (?P<Account_Code>\w+)\s+               
        (?P<Threshold_Income>\d+\.\d{2})?\s*   
        (?P<Min_Hours>\d+\.\d{2})?\s*          
        (?P<Income_Month>\d+\.\d{2})?\s*       
        (?P<Super_Month>\d+\.\d{2})?\s*        
        (?P<Income_Pay>\d+\.\d{2})?\s*         
        (?P<Super_Pay>\d+\.\d{2})?             
    ''', re.VERBOSE)

    # Process each line
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Match a new Loc value
        loc_match = loc_pattern.match(line)
        if loc_match:
            current_loc = loc_match.group('Loc')
            continue

        # Match an employee entry (Emp.Code + Name)
        employee_match = employee_info_pattern.match(line)
        if employee_match:
            current_employee = {
                'Loc': current_loc,
                'Emp.Code': employee_match.group('Emp_Code'),
                'Employee Name': employee_match.group('Employee_Name')
            }
            continue

        # Match payroll detail lines
        detail_match = detail_info_pattern.match(line)
        if detail_match and current_employee:
            row = current_employee.copy()
            row.update({
                'Date Paid': detail_match.group('Date_Paid'),
                'Hours Worked': detail_match.group('Hours_Worked'),
                'Ctrb Type': detail_match.group('Contribution_Type'),
                'Supr Pcnt': detail_match.group('Super_Percent'),
                'Account Code': detail_match.group('Account_Code'),
                'Threshold Income': detail_match.group('Threshold_Income') or "",
                'Monthly Threshold': "",
                'Min Hours': detail_match.group('Min_Hours') or "",
                'Income for Month': detail_match.group('Income_Month') or "",
                'Super for Month': detail_match.group('Super_Month') or "",
                'Income for Pay': detail_match.group('Income_Pay') or "",
                'Super for Pay': detail_match.group('Super_Pay') or ""
            })
            extracted_data.append(row)

    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(extracted_data)

    print(f"✅ CSV file saved: {output_file}")




def process_super_data_23_Onwards(input_file, output_file):
    headers = ['Loc', 'Emp.Code', 'Employee Name', 'Date Paid', 'Hours Worked', 'Ctrb Type',
               'Supr Pcnt', 'Account Code', 'Threshold Income', 'Monthly Threshold',
               'Min Hours', 'Income for Month', 'Super for Month', 'Income for Pay', 'Super for Pay']
    
    # Read the file
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    # Initialize variables
    current_loc = None
    extracted_data = []
    current_employee = None
    
    # Regex patterns
    loc_pattern = re.compile(r'^\s*(?P<Loc>\d+)\s+')
    employee_info_pattern = re.compile(r'^\s*(?P<Emp_Code>\w+)\s+(?P<Employee_Name>[A-Za-z\s\-]+)')
    detail_info_pattern = re.compile(r'''
        (?P<Date_Paid>\d{2}/\d{2}/\d{2})\s+    
        (?P<Hours_Worked>\d+\.\d{2})\s+        
        (?P<Contribution_Type>[A-Z]+)\s+       
        (?P<Super_Percent>\d+\.\d{2})\s+       
        (?P<Account_Code>\w+)\s+               
        (?P<Threshold_Income>\d+\.\d{2})?\s*   
        #(?P<Min_Hours>\d+\.\d{2})?\s*          
        (?P<Income_Month>\d+\.\d{2})?\s*       
        (?P<Super_Month>\d+\.\d{2})?\s*        
        (?P<Income_Pay>\d+\.\d{2})?\s*         
        (?P<Super_Pay>\d+\.\d{2})?             
    ''', re.VERBOSE)

    # Process each line
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Match a new Loc value
        loc_match = loc_pattern.match(line)
        if loc_match:
            current_loc = loc_match.group('Loc')
            continue

        # Match an employee entry (Emp.Code + Name)
        employee_match = employee_info_pattern.match(line)
        if employee_match:
            current_employee = {
                'Loc': current_loc,
                'Emp.Code': employee_match.group('Emp_Code'),
                'Employee Name': employee_match.group('Employee_Name')
            }
            continue

        # Match payroll detail lines
        detail_match = detail_info_pattern.match(line)
        if detail_match and current_employee:
            row = current_employee.copy()
            row.update({
                'Date Paid': detail_match.group('Date_Paid'),
                'Hours Worked': detail_match.group('Hours_Worked'),
                'Ctrb Type': detail_match.group('Contribution_Type'),
                'Supr Pcnt': detail_match.group('Super_Percent'),
                'Account Code': detail_match.group('Account_Code'),
                'Threshold Income': detail_match.group('Threshold_Income') or "",
                'Monthly Threshold': "",
                'Min Hours': "",
                #detail_match.group('Min_Hours') or "",
                'Income for Month': detail_match.group('Income_Month') or "",
                'Super for Month': detail_match.group('Super_Month') or "",
                'Income for Pay': detail_match.group('Income_Pay') or "",
                'Super for Pay': detail_match.group('Super_Pay') or ""
            })
            extracted_data.append(row)

    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(extracted_data)

    print(f"✅ CSV file saved: {output_file}")







# Run code for LABOUR files
process_super_data(input_file_super22, output_file_super22)

process_super_data_23_Onwards(input_file_super23, output_file_super23)

process_super_data_23_Onwards(input_file_super24, output_file_super24)

# Run code for Offshore files
process_super_data_23_Onwards(input_file_super22_offshore, output_file_super22_offshore)

process_super_data_23_Onwards(input_file_super23_offshore, output_file_super23_offshore)

process_super_data_23_Onwards(input_file_super24_offshore, output_file_super24_offshore)

import re
import csv

# File paths
input_file1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.txt"
output_file1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.csv"

# Regex pattern for employee details
employee_info_pattern = re.compile(r'''
    (?P<Location>\w{4})\s+                      # Location (4 characters)
    (?P<Employee_Name>[A-Z\s]+?)\s+             # Employee Name (Uppercase, spaces allowed)
    Leave\s+Start\s+Date:\s+(?P<Leave_Start_Date>\d{2}/\d{2}/\d{2})\s+  
    Hours\s+per\s+Day:\s+(?P<Hours_Per_Day>\d+\.\d{2})\s+  
    (?P<Leave_Code>[A-Za-z\s]+)                 # Leave Code (words like Sick Leave)
''', re.VERBOSE)

# Regex pattern to capture opening balance and closing balance
opening_balance_pattern = re.compile(r'Opening Balance\s+\d{2}/\d{2}/\d{2}\s+.*?\s+(?P<Opening_Balance>-?\d+\.\d+)')
closing_balance_pattern = re.compile(r'Closing Balance\s+\d{2}/\d{2}/\d{2}\s+.*?\s+(?P<Closing_Balance>-?\d+\.\d+)')

# Regex pattern to extract accrual data
detail_info_pattern = re.compile(r'''
    (?P<Detail_Type>Accrual)\s+                 # Accrual type
    (?P<Date>\d{2}/\d{2}/\d{2})\s*              # Accrual date
    .*?                                         # Skip unwanted values
    (?P<Hours_Worked>\d+\.\d{4})\s*             # Hours Worked
    Hours\s+                                    # Required keyword "Hours"
    (?P<Operator>\w+)\s+                        # Operator (e.g., MELISSA)
    (?P<Years>\d+\.\d{2})                       # Years (e.g., 13.77)
''', re.VERBOSE)

# Read the file content while skipping lines containing "Note"
with open(input_file1, "r", encoding="utf-8") as file:
    content = [line for line in file if "Note" not in line]  # Skip lines with "Note"

# Split the content into employee blocks
blocks = re.split(r'(?=\w{4}\s+[\w\s]+?\s+Leave\s+Start\s+Date:)', "\n".join(content))

# Extract the data
extracted_data = []
for block in blocks:
    # Extract employee information
    employee_match = employee_info_pattern.search(block)
    if not employee_match:
        continue  # Skip if no match found

    employee_info = {
        'Loc': employee_match.group('Location'),
        'Employee Name': employee_match.group('Employee_Name'),
        'Leave Start Date': employee_match.group('Leave_Start_Date'),
        'Hours per Day': employee_match.group('Hours_Per_Day'),
        'Leave Code': employee_match.group('Leave_Code'),
        'Opening Balance': '',  # Default empty
        'Closing Balance': ''   # Default empty
    }

    # Extract opening balance
    opening_match = opening_balance_pattern.search(block)
    if opening_match:
        employee_info['Opening Balance'] = opening_match.group('Opening_Balance')

    # Extract closing balance
    closing_match = closing_balance_pattern.search(block)
    if closing_match:
        employee_info['Closing Balance'] = closing_match.group('Closing_Balance')

    # Extract detailed accrual data
    detail_matches = detail_info_pattern.findall(block)
    for detail in detail_matches:
        data_row = employee_info.copy()  # Copy static employee info for each row
        data_row.update({
            'Date': detail[1],  # Date of accrual
            'Hours Worked': detail[2],
            'Operator': detail[3],
            'Years': detail[4]
        })
        extracted_data.append(data_row)

# Define the CSV headers
headers = ['Loc', 'Employee Name', 'Leave Start Date', 'Hours per Day', 'Leave Code', 'Date', 'Hours Worked', 'Operator', 'Years']

# Write to CSV
with open(output_file1, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()  # Write headers first
    writer.writerows(extracted_data)  # Write all data rows

print(f"✅ CSV file has been saved as {output_file1}")



# Leave TXT files 
# Need to revist this still not quite right! - 03/02/2025 

# # File paths
# input_file1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.txt"
# output_file1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.csv"

# # # Regular expression to capture employee information (Loc, Employee Name, Leave Start Date, Hours per Day, Leave Code)
# # employee_info_pattern = re.compile(r'''
# #     (?P<Location>\w{4})\s+                      # Location (e.g., ALDD)
# #     (?P<Employee_Name>[\w\s]+?)\s+               # Employee Name
# #     Leave\s+Start\s+Date:\s+(?P<Leave_Start_Date>\d{2}/\d{2}/\d{2})\s+  # Leave Start Date (e.g., 09/05/08)
# #     Hours\s+per\s+Day:\s+(?P<Hours_Per_Day>\d+\.\d{2})\s+  # Hours per Day (e.g., 7.60)
# #     (?P<Leave_Code>Long\s+Service\s+Leave|Sick\s+Leave|Annual\s+Leave|Rostered\s+Days\s+Off|Study\s+Leave|Compassionate\s+Leave)
# # ''', re.VERBOSE)



# # Corrected regex pattern
# employee_info_pattern_fixed = re.compile(r'''
#     (?P<Location>[A-Z0-9]{4})\s+                       # Location (strictly 4 uppercase letters/numbers)
#     (?P<Employee_Name>[A-Z]+\s+[A-Z]+(?:\s+[A-Z]+)*)   # Employee Name (ensuring proper format)
#     \s+Leave\s+Start\s+Date:\s+(?P<Leave_Start_Date>\d{2}/\d{2}/\d{2})\s+  # Leave Start Date
#     Hours\s+per\s+Day:\s+(?P<Hours_Per_Day>\d+\.\d{2})\s+  # Hours per Day
#     (?P<Leave_Code>Long\s+Service\s+Leave|Sick\s+Leave|Annual\s+Leave|Rostered\s+Days\s+Off|Study\s+Leave|Compassionate\s+Leave)
# ''', re.VERBOSE)

# # Test the pattern on a sample string
# test_string = "ALDD SIMON STEWART Leave Start Date: 09/05/08 Hours per Day: 7.60 Annual Leave"

# match = employee_info_pattern_fixed.search(test_string)
# if match:
#     print(match.groupdict())



# # Regular expression to capture the detailed accrual data
# detail_info_pattern = re.compile(r'''
#     (?P<Detail_Type>\w+)\s+                 # Detail Type (Accrual, Opening Balance, etc.)
#     (?P<Date>\d{2}/\d{2}/\d{2})?\s*         # Optional Date (if present)
#     (?P<Hours_Worked>\d+\.\d{4})?\s*        # Hours Worked (optional)
#     (?P<Entitled_Owing>-?\d+\.\d{4})?\s*    # Entitled Owing (optional)
#     (?P<Pro_Rata_Owing>-?\d+\.\d{4})?\s*    # Pro Rata Owing (optional)
#     (?P<Contingent_Owing>-?\d+\.\d{4})?\s*  # Contingent Owing (optional)
#     Hours\s+                                # Required keyword "Hours"
#     (?P<Operator>\w+)\s+                    # Operator (e.g., MELISSA)
#     (?P<Years>\d+\.\d{2})                   # Years (e.g., 13.77)
# ''', re.VERBOSE)

# # Read the file content
# with open(input_file1, "r", encoding="utf-8") as file:
#     content = file.read()

# # Split the content into employee blocks
# blocks = re.split(r'(?=\w{4}\s+[\w\s]+?\s+Leave\s+Start\s+Date:)', content)

# # Extract the data
# extracted_data = []
# for block in blocks:
#     # Extract employee information
#     #employee_match = employee_info_pattern.search(block)
#     employee_match = employee_info_pattern_fixed.search(block)

#     if employee_match:
#         employee_info = {
#             'Loc': employee_match.group('Location'),
#             'Employee Name': employee_match.group('Employee_Name'),
#             'Leave Start Date': employee_match.group('Leave_Start_Date'),
#             'Hours per Day': employee_match.group('Hours_Per_Day'),
#             'Leave Code': employee_match.group('Leave_Code')
#         }

#     else:
#         print("No match found for block:", block)
#     continue




# # Extract detailed accrual data
# detail_matches = detail_info_pattern.findall(block)
# for detail in detail_matches:
#             data_row = employee_info.copy()  # Copy static employee info for each row
#             data_row.update({
#                 'Date': detail[1] if detail[1] else "",  # Date (if present)
#                 'Hours Worked': detail[2] if detail[2] else "",  # Hours Worked
#                 'Entitled Owing': detail[3] if detail[3] else "",
#                 'Pro Rata Owing': detail[4] if detail[4] else "",
#                 'Contingent Owing': detail[5] if detail[5] else "",
#                 'Operator': detail[6],
#                 'Years': detail[7]
#             })
#             extracted_data.append(data_row)

# # Define the CSV headers
# headers = ['Loc', 'Employee Name', 'Leave Start Date', 'Hours per Day', 'Leave Code', 'Date', 'Hours Worked', 'Entitled Owing', 'Pro Rata Owing', 'Contingent Owing', 'Operator', 'Years']

# # Write to CSV
# with open(output_file1, "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=headers)
#     writer.writeheader()  # Write headers first
#     writer.writerows(extracted_data)  # Write all data rows

# print(f"CSV file has been saved as {output_file1}")


