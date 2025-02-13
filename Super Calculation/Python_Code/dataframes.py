"""
# Super Analysis using Python

## Author: Samuel Smith  
## Date: 04/02/2025  

## Overview:
This Python script performs an in-depth analysis of superannuation data from multiple sources, including payroll records, award coverage, and super clearing house reports. The goal is to validate and ensure accurate superannuation contributions for employees across different financial quarters.

## Key Functionalities:
- **Data Ingestion**: Reads and processes CSV and Excel files for payroll, superannuation, and award coverage.
- **Super Clearing House Analysis**: Aggregates contribution data per financial quarter and employee.
- **Award Coverage Mapping**: Ensures employees are correctly mapped to their respective awards.
- **Payroll Data Validation**: Cross-checks pay codes and superannuation rates to detect inconsistencies.
- **Defined Benefit Fund (DBF) Employees**: Filters and processes employees receiving DBF contributions.

## Data Sources:
1. **Employee_Labels** - Contains employee details including Emp Code, PayPoint, Name, Job Role, Department and Award

2. ### NOT CURRENTLY USED ### **Employee_Leave_History_Report_YY**  - Contains details of employee leave taken.  Columns include:
Loc, Employee Name, Leave Start Date, Hours per Day, Leave Code, Date, Hours Worked, Entitled Owing, Pro Rata Owing, Contingent Owing, Operator, Years

3.  **Pay Details History Report YY** - Payment dates along with paycodes for employees.  Columns include:
Period Ending, Code, Full Name, Pay No., Line, Code, Description, Hours/Value, Pay Rate, Total, Cost Centre, Emp Group 
4. **Superannuation YY** - Contains payment dates of Super for employees including the amounts paid. Columns include: 
Loc, Emp.Code, Employee Name, Date Paid, Hours Worked, Ctrb Type, Supr Pcnt, Account Code, Threshold Income, Monthly Threshold, Min Hours, 
Income for Month, Super for Month, Income for Pay, Super For Pay

4. **Paycode Attributes** 
    - Allownaces_crossEntity -  contains a list of paycodes for allowances with assoicated descriptions, tax status, value and other parameters
    - Contribitins_crossEntity - contains a list of paycodes for contributions to super with assoicated descriptions, tax status, Type, Value etc.
    - Deductions_crossEntity - contains a list of paycodes for Deductions from a employees salary, contribution type, tax status, value etc.
    - Income_crossEntity - contains a list of paycode related to Income Types, Type, Income Category, Time Entry Method etc. 



## Notes:
- Ensure all file paths are correctly set before running the script.
- The script filters out data for the financial quarter '2024 Q4' as per requirements.
- Certain sections (e.g., `empTotal_data`) are placeholders for future use.

"""


 #Super Analysis using Python
import pandas as pd 
import os

Employee_labelsLabour = pd.DataFrame()
#Declare File path for Employee Labels Labour
Employee_labelsLabour = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Employee details\Employee_Labels.csv"
Employee_labelsOffshore = pd.DataFrame()
#Declare File path for Employee Labels Offshore
Employee_labelsOffshore = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Employee details\Employee_Labels.csv"



def process_income_paycodes(file_name): 

    incomePaycodes = pd.DataFrame()
    incomePaycodes = pd.read_csv(file_name)
    # Rename columns for consistency 
    column_mapping = {
        'Income Category' : 'Income_Category',
        'Time Entry Method' :  'Time_Entry_Method', 
        'Reduce Hours' : 'Reduce_Hours'
    }
    incomePaycodes.rename(columns=column_mapping, inplace=True)
    return incomePaycodes

def process_deduction_paycodes(file_name):
    deductionsPaycodes =  pd.DataFrame()
    deductionsPaycodes = pd.read_csv(file_name)

    # Rename columns for consistency 
    column_mapping = {
        'Contribution Type ' : 'Contribution_Type',
        'Tax Status' : 'Tax_Status',
        'Min $' : 'Min_$',
        'Max $' : 'Max_$',
        'Super on Pay Advice' : 'Super_on_Pay_Advice'
    }


    deductionsPaycodes.rename(columns=column_mapping, inplace=True)
    deductionsPaycodes['Value_'] =  deductionsPaycodes['Value_$'].astype(float)
    deductionsPaycodes['Min_$'] = deductionsPaycodes['Min_$'].astype(float)
    deductionsPaycodes['Max_$'] =  deductionsPaycodes['Max_$'].astype(float)
    
    return deductionsPaycodes

def process_contribution_paycodes(file_name):

    contributionPaycodes = pd.DataFrame()
    contributionPaycodes = pd.read_csv(file_name)
    # Rename columns for consistency 
    column_mapping = {
        'Code ' : 'Code',
        'Description ' : 'Description',
        'Tax status' : 'Tax_status',
        'Type' : 'Type',
        'Tax Cert. Status' : 'Tax_Cert_Status',
        'Value $' : 'Value_$',
        'Quarterly Value Maximum' : 'Quarterly_Value_Maximum',
        'Monthly Threshold' : 'Monthly_Threshold',
        'Super for Casuals Under 18' : 'Super_for_Casuals_Under_18',
        'Calculation Table' : 'Calculation_Table',
        'WCOMP' : 'WCOMP',
        'Min $' : 'Min_$',
        'Max $' : 'Max_$',
        'Show rate on Pay Advice' : 'Show_rate_on_Pay_Advice',
        'Show YTD on Pay Advice ' : 'Show_YTD_on_Pay_Advice',
        'Allow Data Entry' : 'Allow_Data_Entry',
        'Multiple G/L Dissections' : 'Multiple_G_L_Dissections',
        'Show on Pay Advice' : 'Show_on_Pay_Advice',
        'Disperse over Cost Centres' : 'Disperse_over_Cost_Centres',
        'Super on Pay Advice' : 'Super_on_Pay_Advice',
        'Frequency' : 'Frequency',
        'Days/Date' : 'Days_Date'
    }

    contributionPaycodes.rename(columns=column_mapping, inplace=True)
    contributionPaycodes['Value_$'] =  contributionPaycodes['Value_$'].astype(float)
    contributionPaycodes['Min_Qty'] = contributionPaycodes['Min_Qty'].astype(float)
    contributionPaycodes['Min_$'] = contributionPaycodes['Min_$'].astype(float)
    contributionPaycodes['Max_$'] =  contributionPaycodes['Max_$'].astype(float)
    contributionPaycodes['Days_Date'] = contributionPaycodes['Days_Date'].astype(int)

    return contributionPaycodes
    
def process_allowance_paycodes(file_name):

    allowancePaycodes = pd.DataFrame()
    # Load data from the file
    allowancePaycodes = pd.read_csv(file_name)  # Replace this with the appropriate function based on your file type


        # Rename columns for consistency
    column_mapping = {
        'Tax Status' : 'Tax_Status',
        'Tax Cert. Status' : 'Tax_Cert_Status',
       'Value $' : 'Value_$',
        'Min Qty' :  'Min_Qty',
        'Max Qty' : 'Max_Qty',
        'Count from' : 'Count_from', 
        'Min $' : 'Min_$', 
        'Max $' : 'Max_$', 
        'Show rate on Pay Advice' : 'Show_rate_on_Pay_Advice',
       'Show YTD on Pay Advice' : 'Show_YTD_on_Pay_Advice',
        'Allow date entry' : 'Allow_date_entry',
       'Multiple G/L Dissections' : 'Multiple_G/L_Dissections',
         'Include in SG Threshold' : 'Include_in_SG_Threshold',
        'Back Pay' : 'Back_Pay'
    }
    allowancePaycodes.rename(columns=column_mapping, inplace=True)

    # Convert Data Types
    allowancePaycodes['Value_$'] =  allowancePaycodes['Value_$'].astype(float)
    allowancePaycodes['Min_Qty'] = allowancePaycodes['Min_Qty'].astype(float)
    allowancePaycodes['Min_$'] = allowancePaycodes['Min_$'].astype(float)
    allowancePaycodes['Max_$'] =  allowancePaycodes['Max_$'].astype(float)

    return allowancePaycodes

#Merge Dataframes with pandas


def process_payroll_data(directory):
    """
    Reads and processes payroll data from multiple CSV files in the given directory.

    Args:
        directory (str): Path to the directory containing payroll CSV files.

    Returns:
        pd.DataFrame: Processed payroll data.
    """
    all_years_payHist = pd.DataFrame()

    # List all files in the directory
    files = [file for file in os.listdir(directory) if file.endswith('.csv')]

    for file in files:
        temp_df = pd.read_csv(os.path.join(directory, file), encoding='latin1', low_memory=False)
        all_years_payHist = pd.concat([all_years_payHist, temp_df], ignore_index=True)

    # Rename columns for consistency
    column_mapping = {
        'Period Ending': 'Period_Ending',
        'Code' : 'Emp.Code',
        'Full Name': 'Full_Name',
        'Pay No.': 'Pay_Number',
        'Code' :  'PayCode',
        'Hours/ Value': 'Hours/Value',
        'Pay Rate': 'Pay_Rate',
        'Cost Centre': 'Cost_Centre',
        'Emp Group': 'Emp_Group'
    }
    all_years_payHist.rename(columns=column_mapping, inplace=True)


    # Drop rows where the 'Code' column has no value (NaN or empty)
    all_years_payHist['Pay_Number'] = all_years_payHist['Pay_Number'].fillna(0).astype(int)

    all_years_payHist.dropna(subset=['Code'], inplace=True)

    # Convert data types
    all_years_payHist['Period_Ending'] = pd.to_datetime(all_years_payHist['Period_Ending'], format='%d/%m/%Y', errors='coerce')
    all_years_payHist['Emp.Code'] = all_years_payHist['Emp.Code'].astype(str)
    all_years_payHist['Emp.Code'] = all_years_payHist['Emp.Code'].str.strip().str.replace(r'\s+', ' ', regex=True).str.upper()
    all_years_payHist['Pay_Number'] = all_years_payHist['Pay_Number'].astype(int)
    all_years_payHist['PayCode'] = all_years_payHist['PayCode'].astype(str)
    all_years_payHist['PayCode'] = all_years_payHist['PayCode'].str.strip().str.replace(r'\s+', ' ', regex=True).str.upper()
    all_years_payHist['Hours/Value'] = all_years_payHist['Hours/Value'].astype(float)
    all_years_payHist['Pay_Rate'] = all_years_payHist['Pay_Rate'].astype(float)
    all_years_payHist['Total'] = all_years_payHist['Total'].astype(float)

    print(all_years_payHist.value_counts())
    print(all_years_payHist.shape)


    return all_years_payHist



def process_super_data(directory):
    """
    Reads and processes Super data from multiple CSV files in the given directory.

    Args:
        directory (str): Path to the directory containing payroll CSV files.

    Returns:
        pd.DataFrame: Super_Labour_data and Super_Offshore_data.
    """
    all_years_super = pd.DataFrame()

    # List all files in the directory
    files = [file for file in os.listdir(directory) if file.endswith('.csv')]

    for file in files:
        temp_df = pd.read_csv(os.path.join(directory, file), encoding='latin1', low_memory=False)
        all_years_super = pd.concat([all_years_super, temp_df], ignore_index=True)

    # Rename columns for consistency
    column_mapping = {
        'Date Paid': 'Date_Paid',
        'Hours Worked': 'Hours_Worked',
        'Ctrb Type': 'Ctrb_Type',
        'Supr Pcnt': 'Supr_Pcnt',
        'Account Code': 'Account_Code',
        'Cost Centre': 'Cost_Centre',
        'Threshold Income': 'Threshold_Income',
        'Monthly Threshold' : 'Monthly_Threshold',
        'Min Hours' : 'Min_Hours',
        'Income for Month' : 'Income_for_Month',
        'Super for Month' : 'Super_for_Month',
        'Income for Pay' : 'Income_for_Pay',
        'Super for Pay' :  'Super_for_Pay'
    }
    all_years_super.rename(columns=column_mapping, inplace=True)

    # Convert data types
    all_years_super['Loc'] = all_years_super['Loc'].astype(str)
    all_years_super['Emp.Code'] = all_years_super['Emp.Code'].astype(str)
    all_years_super['Date_Paid'] = pd.to_datetime(all_years_super['Date_Paid'], format='%d/%m/%Y', errors='coerce')
    all_years_super['Hours_Worked'] = all_years_super['Hours_Worked'].astype(float)
    all_years_super['Ctrb_Type'] = all_years_super['Ctrb_Type'].astype(str)
    all_years_super['Supr_Pcnt'] = all_years_super['Supr_Pcnt'].astype(int)
    all_years_super['Threshold_Income'] = all_years_super['Threshold_Income'].astype(float)
    all_years_super['Min_Hours'] = all_years_super['Min_Hours'].astype(float)
    all_years_super['Income_for_Month'] =  all_years_super['Income_for_Month'].astype(float)
    all_years_super['Super_for_Month'] =   all_years_super['Super_for_Month'].astype(float)
    all_years_super['Income_for_Pay'] = all_years_super['Income_for_Pay'].astype(float)
    all_years_super['Super_for_Pay'] = all_years_super['Super_for_Pay'].astype(float)


    print(all_years_super.value_counts())
    print(all_years_super.shape)

    return all_years_super
















# files = [file for file in os.listdir(r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll")]


# for file in files:
    
#    temp_df = pd.read_csv(os.path.join(r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll", file), encoding='latin1', low_memory=False)
#    all_years_payHist = pd.concat([all_years_payHist, temp_df], ignore_index=True)  # Use ignore_index=True to reset index


# all_years_payHist =  all_years_payHist.rename(columns={'Period Ending' : 'Period_Ending', 'Full Name' : 'Full_Name', 'Pay No.' : 'Pay_Number', 'Hours/ Value' : 'Hours/Value', 
#                                                     'Pay Rate' :  'Pay_Rate', 'Cost Centre' : 'Cost_Centre', 'Emp Group' : 'Emp_Group' })

# all_years_payHist['Period_Ending'] = pd.to_datetime(all_years_payHist['Period_Ending'],   format='%d/%m/%Y', 
#                                                     errors='coerce')

# all_years_payHist['Code'] = all_years_payHist['Code'].apply(str)
# all_years_payHist['Pay_Number'] = all_years_payHist['Pay_Number'].apply(int)
# all_years_payHist['Hours/Value'] = all_years_payHist['Hours/Value'].apply(float)
# all_years_payHist['Pay_Rate'] = all_years_payHist['Pay_Rate'].apply(float)
# all_years_payHist['Total'] = all_years_payHist['Total'].apply(float)


# print(all_years_payHist.value_counts)

# print(all_years_payHist.shape)




payHistoryOffshore = pd.DataFrame()
superLabour = pd.DataFrame()
superOffshore = pd.DataFrame()








Awards = pd.DataFrame()

#Declare file path for Award Coverage
Awards = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Super_Analysis_Python\Awards\5.Award Coverage 15.05.24.csv"

payCodeList = pd.DataFrame()

#Declare the file path for Pay code list
payCodeList = r'C:\\Users\\smits\\OneDrive - SW Accountants & Advisors Pty Ltd\\Desktop\\Super_Analysis_Python\\payCodeList\\Pay-code data.csv'



# Define payroll_data file path
payroll_data = r"C:\\Users\\smits\\OneDrive - SW Accountants & Advisors Pty Ltd\\Desktop\\Super_Analysis_Python\\Payroll\\Payroll data.xlsx"


#Need to see if this sheet needs to be used later in the code 
#empTotal_data = payroll_data["Employee Total"]



superClearningHouseTPD = pd.DataFrame()

superClearningHouseTPD = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Super_Analysis_Python\superClearingHouse\Super Clearing House data.xlsx"

# Read data from Excel for super clearing house sheet called Append1
superClearingHouse = pd.read_excel(
    r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Super_Analysis_Python\superClearingHouse\Super Clearing House data.xlsx",
    sheet_name=['Append1']  # Specifying the sheet to read
)
# Access the specific sheet's data
superClearingHouseData = superClearingHouse['Append1']    



def process_super_clearing_house(super_clearing_house__path, sheet_name, columns_to_drop):
    """
    Load and process the Super Clearing House data from an Excel sheet.

    Args:
        file_path (str): The file path to the Excel file containing the Super Clearing House data.
        sheet_name (str): The name of the sheet to load.
        columns_to_drop (list): A list of column names to drop from the DataFrame.

    Returns:
        pd.DataFrame: The processed Super Clearing House DataFrame with specified columns removed.
    """
    # Read the specified sheet from the Excel file
    super_clearing_house = pd.read_excel(super_clearing_house__path, sheet_name=[sheet_name])
    
    # Access the specific sheet's data
    super_clearing_house_data = super_clearing_house[sheet_name]
    
    # Drop unnecessary columns
    super_clearing_house_data = super_clearing_house_data.drop(columns=columns_to_drop)
    
    return super_clearing_house_data


def get_awards_dataframe(Awards):
    """
    Load and process the Awards DataFrame.

    Args:
        file_path (str): The file path to the Awards CSV file.

    Returns:
        pd.DataFrame: The processed Awards DataFrame with renamed columns, 
                      combined name fields, and cleaned text.
    """
    # Load the Awards DataFrame
    awards = pd.read_csv(Awards)
    
    # Split the 'Position' column into two new columns
    awards[['Position.1', 'Position.2']] = awards['Position'].str.split(' ', n=1, expand=True)
    
    # Define column mapping for renaming
    column_mapping = {
        "Last Name": "Last_Name",
        "First Name": "First_Name",
        "Position.1": "Employee_Code",
        "Position.2": "Employee_Title",
        'Unnamed: 3': 'Employee_Team',
        "Employee Team": "Employee_Team",
        "Award Coverage": "Award_Coverage",
        "Org Manager Name": "Org_Manager_Name",
        "Organizational Unit": "Organizational_Unit",
        "Original Hire Date": "Original_Hire_Date",
        "Last Hire/Rehire Date": "Last_Hire/Rehire_Date",
        "Job Abbrev": "Job_Abbrev",
        "Pay Scale Group": "Pay_Scale_Group",
        "Employee Subgroup": "Employee_Subgroup"
    }
    
    # Rename columns
    awards.rename(columns=column_mapping, inplace=True)
    
    # Combine "Last Name" and "First Name" columns into "Employee_Name"
    awards['Employee_Name'] = awards['Last_Name'] + ' ' + awards['First_Name']
    
    # Drop original "Last_Name" and "First_Name" columns
    awards = awards.drop(columns=['Last_Name', 'First_Name'])
    
    # Define the desired column order
    column_order = [
        "Employee_Name", "Employee_Code", "Employee_Title", "Employee_Team", 
        "Award_Coverage", "Org_Manager_Name", "Organizational_Unit", "Original_Hire_Date", 
        "Last_Hire/Rehire_Date", "Job_Abbrev", "Pay_Scale_Group", "Employee_Subgroup"
    ]
    
    # Reorder columns
    awards = awards[column_order]
    
    # Clean the 'Employee_Name' column: trim whitespace, remove extra spaces, and convert to uppercase
    awards['Employee_Name'] = awards['Employee_Name'].str.strip().str.replace(r'\s+', ' ', regex=True).str.upper()
    
    return awards



def get_pay_code_list(payCodeList):
    """Load and process the Pay Code List DataFrame."""
    pay_code_list = pd.read_csv(payCodeList, encoding='ISO-8859-1')
    columns_to_update = ['TRS - SG Mapping', 'FLUOR - SG Mapping', 'SW - SG mapping']
    pay_code_list[columns_to_update] = pay_code_list[columns_to_update].fillna("N")
    return pay_code_list





def get_emp_pay_period_data(payroll_data):
    """Load and process the Employee Pay Period DataFrame."""
    payroll_data = pd.read_excel(payroll_data, sheet_name="Employee Pay Period")
    payroll_data = payroll_data.astype({
        'Entity': 'string',
        'Location': 'string',
        'Location Desc': 'string',
        'Pay Point': 'string',
        'Pay Point Desc': 'string',
        'Emp Code': 'string',
        'Employee Name': 'string',
        'Pin': 'Int64',
        'Pay Period Quarter': 'string',
        'Advice': 'Int64',
        'Pay Attribute Code': 'string',
        'Pay Attribute Description': 'string'
    })
    payroll_data['PE Date'] = pd.to_datetime(payroll_data['PE Date'], errors='coerce')
    payroll_data['Hrs'] = pd.to_numeric(payroll_data['Hrs'], errors='coerce')
    payroll_data['Amt'] = pd.to_numeric(payroll_data['Amt'], errors='coerce')
    payroll_data = payroll_data[payroll_data['Pay Period Quarter'] != '2024 Q4']
    return payroll_data





def get_super_clearing_house_detail(superClearingHouse):
    """Create the Super Clearing House Detail DataFrame."""
    grouped = superClearingHouse.groupby(
        ["Client Name", "FY Quarter", "PE Date", "Employee Id", "Surname", "First Name", "Location Code", "Cntrbn Desc"]
    )["Cntrbn Amount"].sum().unstack(fill_value=0).reset_index()

    column_order = [
        "Client Name", "FY Quarter", "PE Date", "Employee Id", "Surname", "First Name", "Location Code",
        "SUPER GUARANTEE (SG)", "SALARY SACRIFICE", "SGC ABOVE RATE", 
        "MEMBER DEFINED BENEFITS CONTS", "DEFINED BENEFIT CONTRIBUTIONS",
        "DB COMPULSORY SALARY SACRIFICE"
    ]
    grouped = grouped[column_order]
    grouped = grouped[grouped['PE Date'] > pd.Timestamp('2021-06-30')]
    grouped = grouped[grouped['FY Quarter'] != '2024 Q4']
    return grouped



def get_super_clearing_house_tpd(superClearningHouseTPD):
    """Load and process the TPD Super Clearing House DataFrame."""
    tpd_data = pd.read_excel(superClearningHouseTPD, sheet_name='TPD Super')
    tpd_data['Payroll Number'] = tpd_data['Payroll Number'].astype(str)
    tpd_data['FY Quarter'] = tpd_data['FY Quarter'].astype(str)
    tpd_data['TPD Super'] = pd.to_numeric(tpd_data['TPD Super'], errors='coerce').fillna(0)
    tpd_data = tpd_data[tpd_data['FY Quarter'] != '2024 Q4']
    return tpd_data


# Read the specified sheet from the Excel file
    super_clearing_house = pd.read_excel(super_clearing_house__path, sheet_name=[sheet_name])
    
    # Access the specific sheet's data
    super_clearing_house_data = super_clearing_house[sheet_name]



def get_super_clearing_house_summed(super_clearing_house_detail):
    """
    Group the Super Clearing House Detail DataFrame by FY Quarter and Employee Id,
    and calculate the sum for relevant columns.
    
    Args:
        super_clearing_house_detail (pd.DataFrame): The input DataFrame with detailed clearing house data.
    
    Returns:
        pd.DataFrame: The grouped and aggregated Super Clearing House DataFrame.
    """
    grouped = super_clearing_house_detail.groupby(['FY Quarter', 'Employee Id']).agg({
        'SUPER GUARANTEE (SG)': 'sum',
        'SALARY SACRIFICE': 'sum',
        'DEFINED BENEFIT CONTRIBUTIONS': 'sum',
        'DB COMPULSORY SALARY SACRIFICE': 'sum',
        'MEMBER DEFINED BENEFITS CONTS': 'sum',
        'SGC ABOVE RATE': 'sum'
    }).reset_index()
    
    return grouped


def get_dbf_employees(superClearingHouseData):
    """Create the DBF Employees DataFrame."""
    #dbf_employees = superClearingHouseData.copy()
    dbf_employees = superClearingHouseData
    dbf_employees = dbf_employees[dbf_employees['DEFINED BENEFIT CONTRIBUTIONS'] != 0]
    columns_to_drop = [
        'SUPER GUARANTEE (SG)', 'SALARY SACRIFICE', 'DEFINED BENEFIT CONTRIBUTIONS',
        'DB COMPULSORY SALARY SACRIFICE', 'MEMBER DEFINED BENEFITS CONTS', 'SGC ABOVE RATE'
    ]
    dbf_employees = dbf_employees.drop(columns=columns_to_drop)
    return dbf_employees

