import csv
import re

# Corrected file paths (Use raw string r"" or replace \ with /)
input_file = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Employee details\Employee_Labels.txt"
output_file = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Employee details\Employee_Labels.csv"




with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Define a regex pattern to extract key details
pattern = re.compile(r"Emp\.Code:(\S+)\s+PayPoint:(\S+)\s+(.+?)\s+(\d+.+?)\s+([A-Z]+\s+\d{4} Australia)\s+(.+?)\s+([\w\s\d-]*)")

data = []
headers = ["Emp.Code", "PayPoint", "Name", "Address", "City & Postal Code", "Job Role", "Department"]

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

import re
import csv

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

















# Define headers
#headers = ['Loc', 'Emp.Code', 'Employee Name', 'Date Paid', 'Hours Worked', 'Ctrb Type', 
      #     'Supr Pcnt', 'Account Code', 'Threshold Income', 'Monthly Threshold', 'Min Hours', 
       #    'Income for Month', 'Super for Month', 'Income for Pay', 'Super for Pay']

# headers = ['Loc', 'Emp.Code', 'Employee Name', 'Date Paid', 'Hours Worked', 'Ctrb Type', 
#            'Supr Pcnt', 'Account Code', 'Threshold Income', 
#            'Monthly Threshold',
#             'Min Hours', 
#            'Income for Month', 'Super for Month', 'Income for Pay', 'Super for Pay']

# # Read the file
# with open(input_file_super22, "r", encoding="utf-8") as file:
#     lines = file.readlines()

# # Extract Loc (first number in a section) dynamically
# current_loc = None
# extracted_data = []
# current_employee = None





# # Regex patterns
# #loc_pattern = re.compile(r'^\s*(?P<Loc>\d+)\s*$')  # Match Loc values (e.g., 9)

# #loc_pattern = re.compile(r'^\s*(?P<Loc>\d+)\s+')
# loc_pattern = re.compile(r'^\s*(?P<Loc>\d+)\s+')  # Match Loc values (e.g., 8, 9)


# employee_info_pattern = re.compile(r'^\s*(?P<Emp_Code>\w+)\s+(?P<Employee_Name>[A-Za-z\s\-]+)')  # Match employee rows
# detail_info_pattern = re.compile(r'''
#     (?P<Date_Paid>\d{2}/\d{2}/\d{2})\s+    
#     (?P<Hours_Worked>\d+\.\d{2})\s+        
#     (?P<Contribution_Type>[A-Z]+)\s+       
#     (?P<Super_Percent>\d+\.\d{2})\s+       
#     (?P<Account_Code>\w+)\s+               
#     (?P<Threshold_Income>\d+\.\d{2})?\s*   
#     #(?P<Monthly_Threshold>\d+\.\d{2})?\s*  
#     (?P<Min_Hours>\d+\.\d{2})?\s*          
#     (?P<Income_Month>\d+\.\d{2})?\s*       
#     (?P<Super_Month>\d+\.\d{2})?\s*        
#     (?P<Income_Pay>\d+\.\d{2})?\s*         
#     (?P<Super_Pay>\d+\.\d{2})?             
# ''', re.VERBOSE)

# # Process each line
# for line in lines:
#     line = line.strip()
    
#     # Skip empty lines
#     if not line:
#         continue

#     # Match a new Loc value
#     loc_match = loc_pattern.match(line)
#     if loc_match:
#         current_loc = loc_match.group('Loc')  # Update Loc with new value
#         continue  # Move to the next line

#     # Match an employee entry (Emp.Code + Name)
#     employee_match = employee_info_pattern.match(line)
#     if employee_match:
#         current_employee = {
#             'Loc': current_loc,  # Use current Loc
#             'Emp.Code': employee_match.group('Emp_Code'),
#             'Employee Name': employee_match.group('Employee_Name')
#         }
#         continue  # Move to the next line

#     # Match payroll detail lines (inherit Emp.Code + Name)
#     detail_match = detail_info_pattern.match(line)
#     if detail_match and current_employee:
#         row = current_employee.copy()
#         row.update({
#             'Date Paid': detail_match.group('Date_Paid'),
#             'Hours Worked': detail_match.group('Hours_Worked'),
#             'Ctrb Type': detail_match.group('Contribution_Type'),
#             'Supr Pcnt': detail_match.group('Super_Percent'),
#             'Account Code': detail_match.group('Account_Code'),
#             'Threshold Income': detail_match.group('Threshold_Income') or "",
#             'Monthly Threshold': "",  # Ensure it's in the dictionary
#             'Min Hours': detail_match.group('Min_Hours') or "",
#             'Income for Month': detail_match.group('Income_Month') or "",
#             'Super for Month': detail_match.group('Super_Month') or "",
#             'Income for Pay': detail_match.group('Income_Pay') or "",
#             'Super for Pay': detail_match.group('Super_Pay') or ""
#         })
#         extracted_data.append(row)

# # Write to CSV
# with open(output_file_super22, "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=headers)
#     writer.writeheader()
#     writer.writerows(extracted_data)

# print(f"✅ CSV file saved: {output_file_super22}")


# import csv
# import re

# # File paths
# input_file2 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 22.txt"
# output_file2 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 22.csv"
# # Define headers
# #headers = ['Loc', 'Emp.Code', 'Employee Name', 'Date Paid', 'Hours Worked', 'Ctrb Type', 
#       #     'Supr Pcnt', 'Account Code', 'Threshold Income', 'Monthly Threshold', 'Min Hours', 
#        #    'Income for Month', 'Super for Month', 'Income for Pay', 'Super for Pay']

# headers = ['Loc', 'Emp.Code', 'Employee Name', 'Date Paid', 'Hours Worked', 'Ctrb Type', 
#            'Supr Pcnt', 'Account Code', 'Threshold Income', 
#            'Monthly Threshold',
#             'Min Hours', 
#            'Income for Month', 'Super for Month', 'Income for Pay', 'Super for Pay']

# # Read the file
# with open(input_file2, "r", encoding="utf-8") as file:
#     lines = file.readlines()

# # Extract Loc (first number in a section) dynamically
# current_loc = None
# extracted_data = []
# current_employee = None

# # Regex patterns
# loc_pattern = re.compile(r'^\s*(?P<Loc>\d+)\s+')
#   # Match single-digit Loc values
# employee_info_pattern = re.compile(r'^\s*(?P<Emp_Code>\w+)\s+(?P<Employee_Name>[A-Za-z\s\-]+)')  # Match employee rows
# detail_info_pattern = re.compile(r'''
#     (?P<Date_Paid>\d{2}/\d{2}/\d{2})\s+    
#     (?P<Hours_Worked>\d+\.\d{2})\s+        
#     (?P<Contribution_Type>[A-Z]+)\s+       
#     (?P<Super_Percent>\d+\.\d{2})\s+       
#     (?P<Account_Code>\w+)\s+               
#     (?P<Threshold_Income>\d+\.\d{2})?\s*   
#     #(?P<Monthly_Threshold>\d+\.\d{2})?\s*  
#     (?P<Min_Hours>\d+\.\d{2})?\s*          
#     (?P<Income_Month>\d+\.\d{2})?\s*       
#     (?P<Super_Month>\d+\.\d{2})?\s*        
#     (?P<Income_Pay>\d+\.\d{2})?\s*         
#     (?P<Super_Pay>\d+\.\d{2})?             
# ''', re.VERBOSE)

# # Process each line
# for line in lines:
#     line = line.strip()
    
#     # Skip empty lines
#     if not line:
#         continue

#     # Match a new Loc value
#     loc_match = loc_pattern.match(line)
#     if loc_match:
#         current_loc = loc_match.group('Loc')  # Update Loc
#         continue  # Move to the next line

#     # Match an employee entry (Emp.Code + Name)
#     employee_match = employee_info_pattern.match(line)
#     if employee_match:
#         current_employee = {
#             'Loc': current_loc,  # Use current Loc
#             'Emp.Code': employee_match.group('Emp_Code'),
#             'Employee Name': employee_match.group('Employee_Name')
#         }
#         continue  # Move to the next line

#     # Match payroll detail lines (inherit Emp.Code + Name)
#     detail_match = detail_info_pattern.match(line)
#     if detail_match and current_employee:
#         row = current_employee.copy()
#         row.update({
#             'Date Paid': detail_match.group('Date_Paid'),
#             'Hours Worked': detail_match.group('Hours_Worked'),
#             'Ctrb Type': detail_match.group('Contribution_Type'),
#             'Supr Pcnt': detail_match.group('Super_Percent'),
#             'Account Code': detail_match.group('Account_Code'),
#             'Threshold Income': detail_match.group('Threshold_Income') or "",
#            # 'Monthly Threshold': detail_match.group('Monthly_Threshold') or "",
#             'Min Hours': detail_match.group('Min_Hours') or "",
#             'Income for Month': detail_match.group('Income_Month') or "",
#             'Super for Month': detail_match.group('Super_Month') or "",
#             'Income for Pay': detail_match.group('Income_Pay') or "",
#             'Super for Pay': detail_match.group('Super_Pay') or ""
#         })
#         extracted_data.append(row)

# # Write to CSV
# with open(output_file2, "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=headers)
#     writer.writeheader()
#     writer.writerows(extracted_data)

# print(f"✅ CSV file saved: {output_file2}")










# import csv
# import re

# # File paths
# input_file2 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 22.txt"
# output_file2 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 22.csv"

# # Define headers
# headers = ['Loc', 'Emp.Code', 'Employee Name', 'Date Paid', 'Hours Worked', 'Ctrb Type', 
#            'Supr Pcnt', 'Account Code', 'Threshold Income', 'Monthly Threshold', 'Min Hours', 
#            'Income for Month', 'Super for Month', 'Income for Pay', 'Super for Pay']

# # Employee info regex
# employee_info_pattern = re.compile(r'''
#     (?P<Loc>[A-Z]{3,4})\s+                  # Location (e.g., ALDD)
#     (?P<Employee_Name>[A-Za-z\s\-]+)         # Employee Name (allows spaces and hyphens)
# ''', re.VERBOSE)

# # Detail info regex
# detail_info_pattern = re.compile(r'''
#     (?P<Date_Paid>\d{2}/\d{2}/\d{2})\s+     # Date Paid (DD/MM/YY)
#     (?P<Hours_Worked>\d+\.\d{2})\s+         # Hours Worked (e.g., 50.30)
#     (?P<Contribution_Type>[A-Z]+)\s+        # Contribution Type (e.g., SG)
#     (?P<Super_Percent>\d+\.\d{2})\s+        # Superannuation Percentage (e.g., 10.50)
#     (?P<Account_Code>\w+)\s+                # Account Code (e.g., SGC)
#     (?P<Threshold_Income>\d+\.\d{2})?\s*    # Threshold Income (optional)
#     (?P<Monthly_Threshold>\d+\.\d{2})?\s*   # Monthly Threshold (optional)
#     (?P<Min_Hours>\d+\.\d{2})?\s*           # Minimum Hours (optional)
#     (?P<Income_Month>\d+\.\d{2})?\s*        # Income for Month (optional)
#     (?P<Super_Month>\d+\.\d{2})?\s*         # Super for Month (optional)
#     (?P<Income_Pay>\d+\.\d{2})?\s*          # Income for Pay (optional)
#     (?P<Super_Pay>\d+\.\d{2})?              # Super for Pay (optional)
# ''', re.VERBOSE)

# # Read text file and process it line by line
# with open(input_file2, "r", encoding="utf-8") as file:
#     lines = file.readlines()

# # Skip the first two lines (headers)
# lines = lines[2:]

# # Extract data
# extracted_data = []
# current_employee = None

# for line in lines:
#     line = line.strip()
    
#     # Skip empty lines and summary lines (which contain total values)
#     if not line or re.match(r'^\s*\d+\.\d+\s*$', line):
#         continue

#     # Match employee info
#     employee_match = employee_info_pattern.match(line)
#     if employee_match:
#         loc_value = employee_match.group('Loc')  # Extract Loc value
#         current_employee = {
#             'Loc': loc_value,
#             'Emp.Code': loc_value,  # Copy Loc value into Emp.Code
#             'Employee Name': employee_match.group('Employee_Name')
#         }
#         continue  # Move to the next line for contribution details

#     # Match detail info
#     detail_match = detail_info_pattern.match(line)
#     if detail_match and current_employee:
#         row = current_employee.copy()
#         row.update({
#             'Date Paid': detail_match.group('Date_Paid'),
#             'Hours Worked': detail_match.group('Hours_Worked'),
#             'Ctrb Type': detail_match.group('Contribution_Type'),
#             'Supr Pcnt': detail_match.group('Super_Percent'),
#             'Account Code': detail_match.group('Account_Code'),
#             'Threshold Income': detail_match.group('Threshold_Income') or "",
#             'Monthly Threshold': detail_match.group('Monthly_Threshold') or "",
#             'Min Hours': detail_match.group('Min_Hours') or "",
#             'Income for Month': detail_match.group('Income_Month') or "",
#             'Super for Month': detail_match.group('Super_Month') or "",
#             'Income for Pay': detail_match.group('Income_Pay') or "",
#             'Super for Pay': detail_match.group('Super_Pay') or ""
#         })
#         extracted_data.append(row)

# # Write to CSV
# with open(output_file2, "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=headers)
#     writer.writeheader()
#     writer.writerows(extracted_data)

# print(f"✅ CSV file saved: {output_file2}")





# #Works but needs move across a few columns

# import csv
# import re

# # File paths
# input_file2 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 22.txt"
# output_file2 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 22.csv"

# # Define headers
# headers = ['Loc', 'Emp.Code', 'Employee Name', 'Date Paid', 'Hours Worked', 'Ctrb Type', 
#            'Supr Pcnt', 'Account Code', 'Threshold Income', 'Monthly Threshold', 'Min Hours', 
#            'Income for Month', 'Super for Month', 'Income for Pay', 'Super for Pay']

# # Employee info regex
# employee_info_pattern = re.compile(r'''
#     (?P<Loc>[A-Z]{3,4})\s+                  # Location (e.g., ALDD)
#     (?P<Employee_Name>[A-Za-z\s\-]+)         # Employee Name (allows spaces and hyphens)
# ''', re.VERBOSE)

# # Detail info regex
# detail_info_pattern = re.compile(r'''
#     (?P<Date_Paid>\d{2}/\d{2}/\d{2})\s+     # Date Paid (DD/MM/YY)
#     (?P<Hours_Worked>\d+\.\d{2})\s+         # Hours Worked (e.g., 50.30)
#     (?P<Contribution_Type>[A-Z]+)\s+        # Contribution Type (e.g., SG)
#     (?P<Super_Percent>\d+\.\d{2})\s+        # Superannuation Percentage (e.g., 10.50)
#     (?P<Account_Code>\w+)\s+                # Account Code (e.g., SGC)
#     (?P<Threshold_Income>\d+\.\d{2})?\s*    # Threshold Income (optional)
#     (?P<Monthly_Threshold>\d+\.\d{2})?\s*   # Monthly Threshold (optional)
#     (?P<Min_Hours>\d+\.\d{2})?\s*           # Minimum Hours (optional)
#     (?P<Income_Month>\d+\.\d{2})?\s*        # Income for Month (optional)
#     (?P<Super_Month>\d+\.\d{2})?\s*         # Super for Month (optional)
#     (?P<Income_Pay>\d+\.\d{2})?\s*          # Income for Pay (optional)
#     (?P<Super_Pay>\d+\.\d{2})?              # Super for Pay (optional)
# ''', re.VERBOSE)

# # Read text file and process it line by line
# with open(input_file2, "r", encoding="utf-8") as file:
#     lines = file.readlines()

# # Skip the first two lines (headers)
# lines = lines[2:]

# # Extract data
# extracted_data = []
# current_employee = None

# for line in lines:
#     line = line.strip()
    
#     # Skip empty lines and summary lines (which contain total values)
#     if not line or re.match(r'^\s*\d+\.\d+\s*$', line):
#         continue

#     # Match employee info
#     employee_match = employee_info_pattern.match(line)
#     if employee_match:
#         current_employee = {
#             'Loc': employee_match.group('Loc'),
#             'Emp.Code': '',  # Missing in this format, keeping blank
#             'Employee Name': employee_match.group('Employee_Name')
#         }
#         continue  # Move to the next line for contribution details

#     # Match detail info
#     detail_match = detail_info_pattern.match(line)
#     if detail_match and current_employee:
#         row = current_employee.copy()
#         row.update({
#             'Date Paid': detail_match.group('Date_Paid'),
#             'Hours Worked': detail_match.group('Hours_Worked'),
#             'Ctrb Type': detail_match.group('Contribution_Type'),
#             'Supr Pcnt': detail_match.group('Super_Percent'),
#             'Account Code': detail_match.group('Account_Code'),
#             'Threshold Income': detail_match.group('Threshold_Income') or "",
#             'Monthly Threshold': detail_match.group('Monthly_Threshold') or "",
#             'Min Hours': detail_match.group('Min_Hours') or "",
#             'Income for Month': detail_match.group('Income_Month') or "",
#             'Super for Month': detail_match.group('Super_Month') or "",
#             'Income for Pay': detail_match.group('Income_Pay') or "",
#             'Super for Pay': detail_match.group('Super_Pay') or ""
#         })
#         extracted_data.append(row)

# # Write to CSV
# with open(output_file2, "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=headers)
#     writer.writeheader()
#     writer.writerows(extracted_data)

# print(f"✅ CSV file saved: {output_file2}")





# # File paths
# input_file2 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 22.txt"
# output_file2  = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\Superannuation 22.csv"




# headers = ['Ctrb.Code Loc', 'Emp.Code', 'Description Employee Name', 'Date Paid', 'Hours Worked', 'Ctrb Type', 'Supr Pcnt', 'Account Code', 'Threshold Income', 'Monthly Threshold', 
           
#            'Min Hours', 'Income for Month', 'Super for Month', 'Income for Pay', 'Super for Pay']



# employee_info_pattern = re.compile(r'''
#     (?P<Location>\w{3,4})\s+                          # Location (e.g., ALDD)
#     (?P<Employee_Name>[A-Z][A-Za-z\s\-']+)            # Employee Name (supports spaces, hyphens, apostrophes)
# ''', re.VERBOSE)


# detail_info_pattern = re.compile(r'''
#     (?P<Date_Paid>\d{2}/\d{2}/\d{2})\s+       # Date Paid (DD/MM/YY)
#     (?P<Hours_Worked>\d+\.\d{2})\s+           # Hours Worked (e.g., 50.30)
#     (?P<Contribution_Type>[A-Z]+)\s+          # Contribution Type (e.g., SG)
#     (?P<Super_Percent>\d+\.\d{2})\s+          # Superannuation Percentage (e.g., 10.50)
#     (?P<Account_Code>\w+)\s+                  # Account Code (e.g., SGC)
#     (?P<Threshold_Income>\d+\.\d{2})?\s*      # Threshold Income (optional)
#     (?P<Monthly_Threshold>\d+\.\d{2})?\s*     # Monthly Threshold (optional)
#     (?P<Min_Hours>\d+\.\d{2})?\s*             # Minimum Hours (optional)
#     (?P<Income_Month>\d+\.\d{2})?\s*          # Income for Month (optional)
#     (?P<Super_Month>\d+\.\d{2})?\s*           # Super for Month (optional)
#     (?P<Income_Pay>\d+\.\d{2})?\s*            # Income for Pay (optional)
#     (?P<Super_Pay>\d+\.\d{2})?                # Super for Pay (optional)
# ''', re.VERBOSE)





# # Read the text file
# with open(input_file2, "r", encoding="utf-8") as file:
#     content = file.read()

# # Split by employees
# blocks = re.split(r"(?=\w{3,4}\s+[A-Z][A-Za-z\s\-\']+)", content)


# # Extract data
# extracted_data = []
# for block in blocks:
#     employee_match = employee_info_pattern.search(block)
#     if employee_match:
#         employee_info = {
#             'Ctrb.Code Loc': employee_match.group('Ctrb.Code Loc'),
#             'Emp.Code': employee_match.group('Emp.Code')
#         }

#         # Find all contribution details for this employee
#         detail_matches = detail_info_pattern.findall(block)
#         for detail in detail_matches:
#             row = employee_info.copy()  # Copy static data
#             row.update({
#                 'Date Paid': detail[0],
#                 'Hours Worked': detail[1],
#                 'Ctrb Type': detail[2],
#                 'Supr Pcnt': detail[3],
#                 'Account Code': detail[4],
#                 'Threshold Income': detail[5] if detail[5] else "",
#                 'Monthly Threshold': detail[6] if detail[6] else "",
#                 'Min Hours': detail[7] if detail[7] else "",
#                 'Income for Month': detail[8] if detail[8] else "",
#                 'Super for Month': detail[9] if detail[9] else "",
#                 'Income for Pay': detail[10] if detail[10] else "",
#                 'Super for Pay': detail[11] if detail[11] else ""
#             })
#             extracted_data.append(row)

# # Write to CSV
# with open(output_file2, "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=headers)
#     writer.writeheader()
#     writer.writerows(extracted_data)

# print(f"✅ CSV file saved: {output_file2}")















# Leave TXT files 
# Need to revist this still not quite right! - 03/02/2025 

# File paths
input_file1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.txt"
output_file1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.csv"

# Regular expression to capture employee information (Loc, Employee Name, Leave Start Date, Hours per Day, Leave Code)
employee_info_pattern = re.compile(r'''
    (?P<Location>\w{4})\s+                      # Location (e.g., ALDD)
    (?P<Employee_Name>[\w\s]+?)\s+               # Employee Name
    Leave\s+Start\s+Date:\s+(?P<Leave_Start_Date>\d{2}/\d{2}/\d{2})\s+  # Leave Start Date (e.g., 09/05/08)
    Hours\s+per\s+Day:\s+(?P<Hours_Per_Day>\d+\.\d{2})\s+  # Hours per Day (e.g., 7.60)
    (?P<Leave_Code>Long\s+Service\s+Leave|Sick\s+Leave|Annual\s+Leave|Rostered\s+Days\s+Off|Study\s+Leave|Compassionate\s+Leave)
''', re.VERBOSE)

# Regular expression to capture the detailed accrual data
detail_info_pattern = re.compile(r'''
    (?P<Detail_Type>\w+)\s+                 # Detail Type (Accrual, Opening Balance, etc.)
    (?P<Date>\d{2}/\d{2}/\d{2})?\s*         # Optional Date (if present)
    (?P<Hours_Worked>\d+\.\d{4})?\s*        # Hours Worked (optional)
    (?P<Entitled_Owing>-?\d+\.\d{4})?\s*    # Entitled Owing (optional)
    (?P<Pro_Rata_Owing>-?\d+\.\d{4})?\s*    # Pro Rata Owing (optional)
    (?P<Contingent_Owing>-?\d+\.\d{4})?\s*  # Contingent Owing (optional)
    Hours\s+                                # Required keyword "Hours"
    (?P<Operator>\w+)\s+                    # Operator (e.g., MELISSA)
    (?P<Years>\d+\.\d{2})                   # Years (e.g., 13.77)
''', re.VERBOSE)

# Read the file content
with open(input_file1, "r", encoding="utf-8") as file:
    content = file.read()

# Split the content into employee blocks
blocks = re.split(r'(?=\w{4}\s+[\w\s]+?\s+Leave\s+Start\s+Date:)', content)

# Extract the data
extracted_data = []
for block in blocks:
    # Extract employee information
    employee_match = employee_info_pattern.search(block)
    if employee_match:
        employee_info = {
            'Loc': employee_match.group('Location'),
            'Employee Name': employee_match.group('Employee_Name'),
            'Leave Start Date': employee_match.group('Leave_Start_Date'),
            'Hours per Day': employee_match.group('Hours_Per_Day'),
            'Leave Code': employee_match.group('Leave_Code')
        }

        # Extract detailed accrual data
        detail_matches = detail_info_pattern.findall(block)
        for detail in detail_matches:
            data_row = employee_info.copy()  # Copy static employee info for each row
            data_row.update({
                'Date': detail[1] if detail[1] else "",  # Date (if present)
                'Hours Worked': detail[2] if detail[2] else "",  # Hours Worked
                'Entitled Owing': detail[3] if detail[3] else "",
                'Pro Rata Owing': detail[4] if detail[4] else "",
                'Contingent Owing': detail[5] if detail[5] else "",
                'Operator': detail[6],
                'Years': detail[7]
            })
            extracted_data.append(data_row)

# Define the CSV headers
headers = ['Loc', 'Employee Name', 'Leave Start Date', 'Hours per Day', 'Leave Code', 'Date', 'Hours Worked', 'Entitled Owing', 'Pro Rata Owing', 'Contingent Owing', 'Operator', 'Years']

# Write to CSV
with open(output_file1, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()  # Write headers first
    writer.writerows(extracted_data)  # Write all data rows

print(f"CSV file has been saved as {output_file1}")


# import re
# import csv

# # File paths
# input_file1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.txt"
# output_file1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.csv"

# # Regular expression to capture employee information (Loc, Employee Name, Leave Start Date, etc.)
# employee_info_pattern = re.compile(r'''
#     (?P<Location>\w{4})\s+                      # Location (e.g., ALDD)
#     (?P<Employee_Name>[\w\s]+?)\s+               # Employee Name
#     (?P<Leave_Type>Leave\s+Start\s+Date:)\s+     # Leave Type
#     (?P<Leave_Start_Date>\d{2}/\d{2}/\d{2})\s+  # Leave Start Date (e.g., 09/05/08)
#     (?P<Hours_Per_Day_Label>Hours\s+per\s+Day:)\s+
#     (?P<Hours_Per_Day>\d+\.\d{2})\s*             # Hours per Day (e.g., 7.60)
# ''', re.VERBOSE)

# # Regular expression to capture the detailed rows (Hours, Entitled, Pro Rata, etc.)
# detail_info_pattern = re.compile(r'''
#     (?P<Detail_Type>\w+)\s+                 # Detail Type (Accrual, Opening Balance, etc.)
#     (?P<Entitled_Owing>\d+\.\d{4})\s+      # Entitled Owing (e.g., 0.0000)
#     (?P<Pro_Rata_Owing>\d+\.\d{4})\s+      # Pro Rata Owing (e.g., 0.0000)
#     (?P<Contingent_Owing>\d+\.\d{4})\s+    # Contingent Owing (e.g., 0.0000)
#     (?P<Leave_Code>Hours|Sick|Annual)\s+   # Leave Code (e.g., Hours)
#     (?P<Operator>\w+)\s+                   # Operator (e.g., MELISSA)
#     (?P<Years>\d+\.\d{2})                  # Years (e.g., 13.77)
# ''', re.VERBOSE)

# # Read the file content
# with open(input_file1, "r", encoding="utf-8") as file:
#     content = file.read()

# # Split the content into blocks for each employee (assuming each block starts with Location and Employee Name)
# blocks = re.split(r'(?=\w{4}\s+[\w\s]+?\s+Leave\s+Start\s+Date:)', content)

# # Extract the data from each block
# extracted_data = []
# for block in blocks:
#     # Extract the first line (employee info)
#     employee_match = employee_info_pattern.search(block)
#     if employee_match:
#         employee_info = {
#             'Loc': employee_match.group('Location'),
#             'Employee Name': employee_match.group('Employee_Name'),
#             'Leave Start Date': employee_match.group('Leave_Start_Date'),
#             'Hours per Day': employee_match.group('Hours_Per_Day'),
#         }

#         # Now, extract the detailed rows (Accruals, Entitlements, etc.)
#         detail_matches = detail_info_pattern.findall(block)
#         for detail in detail_matches:
#             data_row = employee_info.copy()  # Copy the employee info to each row
#             data_row.update({
#                 'Entitled Owing': detail[1],
#                 'Pro Rata Owing': detail[2],
#                 'Contingent Owing': detail[3],
#                 'Leave Code': detail[4],
#                 'Operator': detail[5],
#                 'Years': detail[6]
#             })
#             extracted_data.append(data_row)

# # Define the CSV headers
# headers = ['Loc', 'Employee Name', 'Leave Start Date', 'Hours per Day', 'Entitled Owing', 'Pro Rata Owing', 'Contingent Owing', 'Leave Code', 'Operator', 'Years']

# # Write to CSV
# with open(output_file1, "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=headers)
#     writer.writeheader()  # Write headers first
#     writer.writerows(extracted_data)  # Write all rows of data

# print(f"CSV file has been saved as {output_file1}")



# import re
# import csv

# # File paths
# input_file1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.txt"
# output_file1 = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Leave\Employee_Leave_History_Report 22.csv"

# # Regular expression to capture employee information (Loc, Employee Name, Leave Start Date, etc.)
# employee_info_pattern = re.compile(r'''
#     (?P<Location>\w{4})\s+                      # Location (e.g., ALDD)
#     (?P<Employee_Name>[\w\s]+?)\s+               # Employee Name
#     (?P<Leave_Type>Leave\s+Start\s+Date:)\s+     # Leave Type
#     (?P<Leave_Start_Date>\d{2}/\d{2}/\d{2})\s+  # Leave Start Date (e.g., 09/05/08)
#     (?P<Hours_Per_Day_Label>Hours\s+per\s+Day:)\s+
#     (?P<Hours_Per_Day>\d+\.\d{2})\s*             # Hours per Day (e.g., 7.60)
# ''', re.VERBOSE)

# # Regular expression to capture the detailed rows (Hours, Entitled, Pro Rata, etc.)
# detail_info_pattern = re.compile(r'''
#     (?P<Detail_Type>\w+)\s+                 # Detail Type (Accrual, Opening Balance, etc.)
#     (?P<Entitled_Owing>\d+\.\d{4})\s+      # Entitled Owing (e.g., 0.0000)
#     (?P<Pro_Rata_Owing>\d+\.\d{4})\s+      # Pro Rata Owing (e.g., 0.0000)
#     (?P<Contingent_Owing>\d+\.\d{4})\s+    # Contingent Owing (e.g., 0.0000)
#     (?P<Leave_Code>Hours|Sick|Annual)\s+   # Leave Code (e.g., Hours)
#     (?P<Operator>\w+)\s+                   # Operator (e.g., MELISSA)
#     (?P<Years>\d+\.\d{2})                  # Years (e.g., 13.77)
# ''', re.VERBOSE)

# # Read the file content
# with open(input_file1, "r", encoding="utf-8") as file:
#     content = file.read()

# # Split the content into blocks for each employee (assuming each block starts with Location and Employee Name)
# blocks = re.split(r'(?=\w{4}\s+[\w\s]+?\s+Leave\s+Start\s+Date:)', content)

# # Extract the data from each block
# extracted_data = []
# for block in blocks:
#     # Extract the first line (employee info)
#     employee_match = employee_info_pattern.search(block)
#     if employee_match:
#         employee_info = {
#             'Loc': employee_match.group('Location'),
#             'Employee Name': employee_match.group('Employee_Name'),
#             'Date': employee_match.group('Leave_Start_Date'),
#             'Hours Worked': employee_match.group('Hours_Per_Day'),
#         }

#         # Now, extract the detailed rows (Accruals, Entitlements, etc.)
#         detail_matches = detail_info_pattern.findall(block)
#         for detail in detail_matches:
#             data_row = employee_info.copy()  # Copy the employee info to each row
#             data_row.update({
#                 'Entitled Owing': detail[1],
#                 'Pro Rata Owing': detail[2],
#                 'Contingent Owing': detail[3],
#                 'Leave Code': detail[4],
#                 'Operator': detail[5],
#                 'Years': detail[6]
#             })
#             extracted_data.append(data_row)

# # Define the CSV headers
# headers = ['Loc', 'Employee Name', 'Date', 'Hours Worked', 'Entitled Owing', 'Pro Rata Owing', 'Contingent Owing', 'Leave Code', 'Operator', 'Years']

# # Write to CSV
# with open(output_file1, "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=headers)
#     writer.writeheader()  # Write headers first
#     writer.writerows(extracted_data)  # Write all rows of data

# print(f"CSV file has been saved as {output_file1}")





# output_cleaned_data = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Project Daylight\Outputs\Cleaned Data\\"





# def txt_to_csv(input_file: str, output_file: str, regex_pattern: str):
#     """
#     Reads a text file, extracts relevant data using a provided regex pattern,
#     and writes the cleaned data into a CSV file.
    
#     :param input_file: Path to the input text file.
#     :param output_file: Path to save the output CSV file.
#     :param regex_pattern: Regular expression pattern to extract structured data.
#     """
#     with open(input_file, "r", encoding="utf-8") as f:
#         lines = f.readlines()
    
#     pattern = re.compile(regex_pattern)
#     data = []
    
#     # Extract headers from the first valid row
#     for line in lines:
#         match = pattern.search(line)
#         if match:
#             headers = [field.split(':')[0] if ':' in field else f"Column{i+1}" for i, field in enumerate(match.groups())]
#             break
#     else:
#         print("No valid data extracted. Check your regex pattern and input file.")
#         return
    
#     # Extract data from all matching rows
#     for line in lines:
#         match = pattern.search(line)
#         if match:
#             data.append([field.strip() for field in match.groups()])
    
#     # Write to CSV
#     with open(output_file, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(headers)
#         writer.writerows(data)
    
#     print(f"CSV file has been saved as {output_file}")







# Example usage
# regex_pattern = r"Emp\.Code:(\S+)\s+PayPoint:(\S+)\s+([^\d]+?)\s+(\d+.+?)\s+([A-Z]+\s+\d{4} Australia)\s+([A-Za-z]+)\s+([A-Za-z\d\s-]*)"
# process_text_to_csv("input.txt", "output.csv", regex_pattern)
# # Example usage
# regex_pattern = r"Emp\.Code:(\S+)\s+PayPoint:(\S+)\s+([^\d]+?)\s+(\d+.+?)\s+([A-Z]+\s+\d{4} Australia)\s+([A-Za-z]+)\s+([A-Za-z\d\s-]*)"
# txt_to_csv(input_file, output_file, regex_pattern)
