import csv
import re

# Corrected file paths (Use raw string r"" or replace \ with /)
input_file = r'C:\Users\smits\Downloads\Employee_Labels.txt'
output_file = r'C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Super_Analysis_Python\Maritimo Dataset cleaning\Employee_Labels.csv'




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
