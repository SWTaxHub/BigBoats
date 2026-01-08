import sys
print(sys.executable)

import re

import os
from dataframes import(
    # process_income_paycodes,
    # process_deduction_paycodes,
    # process_contribution_paycodes,
    # process_allowance_paycodes,
    process_payroll_data,
    process_super_data
    
)
import pandas as pd
import numpy as np
from pandas import ExcelWriter  




# File paths
#Declare File path for Labour Payroll
Payroll_Labour_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll\November Files"

#Declare File path for Offshore Payroll
Payroll_Offshore_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Payroll\November Files"


#Declare File path for Allowance Paycodes 
allowancePaycodes_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\Allowances_crossEntity.csv"
#Declare File path for Contribution Paycodes 
contributionPaycodes_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\Contributions_crossEntity.csv"
#Declare File path for Deductions Paycodes 
deductionsPaycodes_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\Deductions_crossEntity.csv"
#Declare File path for Income Paycodes 
incomePaycodes_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\Income_crossEntity.csv"
#Declare File path for Employee Labels Labour
Employee_labelsLabour_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Employee details\Employee_Labels.csv"
#Declare File path for Employee Labels Offshore
Employee_labelsOffshore_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Employee details\Employee_Labels.csv"
# Declare File path for Super Labour
Super_Labour_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\CSVs"
# Declare file path for super offshore
Super_Offshore_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Super\CSVs"
# Declare file path for combo paycodes


# Generate DataFrames for Payroll
Payroll_Labour_data = process_payroll_data(Payroll_Labour_filepath)
Payroll_Labour_data.to_csv('Payroll_Labour_data_load.csv', index=False)

Payroll_Offshore_data = process_payroll_data(Payroll_Offshore_filepath)
# Generate DataFrames for Super
Super_Labour_data = process_super_data(Super_Labour_filepath)
Super_Offshore = process_super_data(Super_Offshore_filepath)




# # # # Start of Merge DataFrames for Labour and Offshore Payroll
# # # Business Logic overview
""" 
1. Financial Year & Quarter Rules

Australian Financial Year: Runs from 1 July to 30 June.
Quarter Mapping:

Q1: July–September
Q2: October–December
Q3: January–March
Q4: April–June


Labour Exception: If the record is flagged as LABOUR and falls on or after 28 June 2024, it is treated as Q1 of the next financial year.


2. SG (Superannuation Guarantee) Rate

SG contribution rates are hard-coded by financial year:

FY2021 → 9.5%
FY2022 → 10%
FY2023 → 10.5%
FY2024 → 11%
FY2025 → 11.5%
FY2026 → 12%


Assumes these rates apply uniformly across all employees and pay codes for that year.


3. Paycode Mapping Logic

Paycodes are categorised based on an external mapping file:

Client Mapping: Paycodes marked as SG-relevant for client reporting.
SW Mapping:

OTE → Ordinary Time Earnings
S&W → Salaries & Wages
SUPER - SG → Superannuation contributions
TAX → Tax-related codes




Assumes mapping file is accurate and up to date.


4. OTE and SG Calculations

OTE buckets: Amounts classified as OTE or S&W are summed without caps.
Expected SG: Calculated as OTE amount × SG rate for both Client and SW mappings.
Actual SG Paid: Derived from paycodes mapped to SUPER - SG.
Discrepancy: Difference between Client and SW expected SG is tracked for reconciliation.


5. Data Cleansing

Removes rows for:

Specific employee names (likely test or non-payroll entries).
Keywords indicating adjustments, corrections, or non-standard payments (e.g., “BACKPAY”, “UNPAID”, “CORRECTION”).


Assumes these exclusions are correct and do not affect compliance reporting.


6. Output

Creates a unique identifier per employee per quarter (QtrEMPLID).
Saves processed data to CSV for downstream reporting or audit. 
"""

def payroll_calc(Payroll_Labour_data, file_suffix="LABOUR / OFFSHORE"):
    """
    Normalise and clean key fields.
    Derive financial year and quarter labels.
    Map pay codes to categories (OTE, S&W, Super, Tax).
    Calculate expected and actual superannuation (SG) amounts.
    Output a processed CSV for reporting.
    """
    # Work on a copy; avoid globals
    payroll_data = Payroll_Labour_data.copy()

    # ---- 0) Basic column checks & normalization ----
    # Use Description_x if present (typical after merges); else Description
    
    required_cols = [
        'Pay_Number', 'Period_Ending', 'Pay Description', 'Amount', 'Code', 'Full_Name', 'Unique_Key'
    ]
    missing = [c for c in required_cols if c not in payroll_data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Ensure Period_Ending is datetime
    payroll_data['Period_Ending'] = pd.to_datetime(payroll_data['Period_Ending'], errors='coerce')

    # ---- 1) Quarter & Financial Year ----

    month = payroll_data['Period_Ending'].dt.month
    day   = payroll_data['Period_Ending'].dt.day
    year  = payroll_data['Period_Ending'].dt.year

    # Quarter logic with Labour exception
    payroll_data['FY_Q'] = np.where(
        (payroll_data['Weird_FY_Check'] == 'LABOUR') & (month == 6) & (day >= 28) & (year == 2024), 'Q1',  # Exception for Labour
        np.where(
            month.isin([7, 8, 9]), 'Q1',
            np.where(
                month.isin([10, 11, 12]), 'Q2',
                np.where(
                    month.isin([1, 2, 3]), 'Q3',
                    np.where(month.isin([4, 5, 6]), 'Q4', 'Unknown')
                )
            )
        )
    )

    # Financial Year logic with Labour exception
    payroll_data['Financial_Year'] = np.where(
        (payroll_data['Weird_FY_Check'] == 'LABOUR') & (month == 6) & (day >= 28) & (year == 2024), year + 1,  # Exception for Labour
        np.where(
            month >= 7,
            year + 1,
            year
        )
    )



    # Convert Financial_Year to integer
    payroll_data['Financial_Year'] = payroll_data['Financial_Year'].fillna(0).astype(int)

    payroll_data['FY_Q_Label'] = 'FY' + payroll_data['Financial_Year'].astype(str) + '_' + payroll_data['FY_Q']

    # ---- 2) SG rate by FY ----
    sg_map = {2021: 0.095, 2022: 0.10, 2023: 0.105, 2024: 0.11, 2025: 0.115, 2026: 0.12}
    payroll_data['SG_Rate'] = payroll_data['Financial_Year'].map(sg_map).astype(float)

    # ---- 3) Paycode mapping ----
    # Update this path if needed
    paymap_path = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Client Projects\Maritimo\2025.05.21_PAYCODE_MAPPING.xlsx"
    paycode_mapping = pd.read_excel(paymap_path, sheet_name='UPDATED MAPPING', engine='openpyxl')
    
  

 


    # --- Patterns ---
    DATE_LEADING = r'^\s*\d{1,2}/\d{1,2}/\d{2,4}\s*'  # e.g., 25/04/23 or 25/04/2023 at the start
    NUM_OR_CURRENCY = r'(?:\$?\d)'                    # token that begins with $ or a digit

    def clean_pay_description(series: pd.Series) -> pd.Series:
            s = (
                series.astype('string')
                    .str.replace('\xa0', ' ', regex=False)              # non-breaking spaces -> normal
                    .str.replace(DATE_LEADING, '', regex=True)          # remove leading date
                    .str.strip()
            )

                # Case A: description starts with a letter -> keep only the initial text
            mask_alpha = s.str.match(r'^[A-Za-z]')
            s_alpha = s[mask_alpha]

                # Extract initial alphabetic phrase that is immediately followed by a space + number/currency
                # If no number follows, we keep the whole alpha-leading string (e.g., "Public Holiday").
            extracted = s_alpha.str.extract(
                    r'^\s*([A-Za-z][A-Za-z %&()\-\/]*?)(?=\s+' + NUM_OR_CURRENCY + r')',
                    expand=False
                )
            s.loc[mask_alpha] = extracted.fillna(s_alpha)

                # Tidy whitespace everywhere
            s = s.str.replace(r'\s{2,}', ' ', regex=True).str.strip()

            return s

        # --- Usage on your dataframe ---
    payroll_data['Cleaned_Description'] = clean_pay_description(payroll_data['Pay Description'])
    payroll_data['Pay Description'] = payroll_data['Cleaned_Description']

    

    # Clean Pay Description so all caps and trimmed
    payroll_data['Pay Description'] = payroll_data['Pay Description'].str.upper().str.strip()


# Drop lines for payment processing lines for data cleansing
    drop_names =[
        'AARON MCKENNA' ,
        'AIDAN HIGGINS',
        'AMBER WATT',
        'ANDREW GREEN' ,
        'ANDREW SHUTTLEWORTH' ,
        'ANN MEURS' ,
        'AUSTIN GROOBY' ,
        'BAILEY READ' ,
        'BENJIE JENSEN' ,
        'BRANDON RILEY' ,
        'CAILAN MCCOSH' ,
        'CAMERON KELTON' ,
        'CARLY S GAMBOA' ,
        'CHRISTIAN WECH' ,
        'DAMIAN & LAINE BURTT' ,
        'DANIEL MOORE' ,
        'DARREN CADMAN' ,
        'DERRICK NOWAK' ,
        'DREW HEADLEY' ,
        'DYLAN BOOL' ,
        'GARRETT GRIFFITHS' ,
        'GREG STROUD' ,
        'ISAAC MANN' ,
        'JAC HARMAN' ,
        'JACK SUTHERLAND' ,
        'JACK HASHFIELD' ,
        'JACOB SAVERIN' ,
        'JACOB ROLAND' ,
        'JAKE READ' ,
        'JAMES LOHMANN' ,
        'JAYDEN ZAKAZAKAARCHER' ,
        'JAYE LABRUM' ,
        'JOEL DONNELLY' ,
        'JOHN CLAYTON' ,
        'JONATHAN WALTER' ,
        'JORDAN SHILLINGFORD' ,
        'JORDAN HANSON' ,
        'JORDAN STEWART' ,
        'JORDAN LEE' ,
        'JORDAN GOMEZ' ,
        'KADE M MACNAB' ,
        'JACKSON BRYANT-KELLY' ,
        'KIEREN DOORTY' ,
        'KOMANG & SHARON SUASTIKA' ,
        'KYNAN MCKENZIE' ,
        'LACHLAN ANWYL' ,
        'LACHLAN RIDER' ,
        'LARA COX' ,
        'LUCAS ZYSVELT' ,
        'LUCAS BOUHET' ,
        'MAHMOUD ZEINELDIN' ,
        'MARK PRICE' ,
        'MATTHEW DUNCAN' ,
        'MATTHEW HAYMAN' ,
        'MATTHEW WARREN' ,
        'MAX A FINDLAY' ,
        'MICHAEL COX' ,
        'MICHAEL SCHEYER' ,
        'REECE DILNUTT' ,
        'ROBERT HALL' ,
        'ROBERT SZIGYARTO' ,
        'ROBERT VERMUELEN' ,
        'ROEDOLF KOTZE' ,
        'RYAN NICHOLS' ,
        'RYAN ELLIS' ,
        'STEPHAN & AMBER CANTRICK' ,
        'TY JORDAN' ,
        'TYLER RUTTER' ,
        'ZOE ELIS ANNA DE PRYCK',
        'BRODIE RUTTER',
        'CHELCIE JONES',
        'CHERYL-ANN MEURS',
        'COLIN JOHN MCKAY',
        'DESTINY EARL',
        'GRANT BARRY-COTTER',
        'JACK SOUTER',
        'JASMINE FULLER',
        'JM BLACKLEY',
        'MICHAEL LLOYD',
        'T BARRY COTTER',
        'DARREN & NIKI BLENKINS',
        'SOYEON CHOI',
        'SARAH SATIU',
        'COTTER (BARG)',
        'ANA LIMA ROXO',
        # Over lines to drop
        '2ND YEAR',
        '6 HOURS',
        'BACKPAY W/E',
        'BONUS NOT PREVIOUSLY',
        'CORRECTED FROM PREVIOUS',
        'DAYS',
        'CORRECTED',
        'CORRECTION WE',
        'FOR MON',
        'FOR',
        'ENDING',
        'FOR WEEK ENDING',
        'EFFECTIVE',
        'FROM',
        'G AND M JONES',
        'HOURS NOT PAID',
        'HOURS SHORT PAID',
        'IN LIEU OF',
        'OF',
        'LEAVE PAID ON',
        'NOT PAID',
        'OF HOURLY',
        'OF SICK',
        'OF W/E',
        'LEAVE SHORT PAID',
        'OF SL',
        'OF AL -',
        'OF ANNUAL',
        'OF PAY',
        'SHORT PAID',
        'PAY RATE AS',
        'PAY FROM',
        'RATE AS',
        'PAY RATE',
        'PAY FOR PUBLIC HOL',
        'PAY',
        'UNPAID',
        'PAYMENT',
        'SHORTPAID',
        'PAID OUT ON MEDICAL',
        'WORKED',
        'ADJUSTMENT FOR TIME OFF'
        'ANNUAL LEAVE LOAADING',
        'APPRENTICESHIP NEW',
        'LEAVE LOADING',
        'MEAL ALLOW',
        'ACKNOWLEDGEMENT',
        'C D YOUNGS',
        'C A JONES',
        'GG & LJ ZISCHKE',
        'JIG & RG CORBITT',
        'MR PHILIP CANDLER',
        'PHILIP CANDLER'

            ]



    payroll_data = payroll_data[~payroll_data['Pay Description'].isin(drop_names)]

    
    cond = payroll_data['Pay Description'].eq('NORMAL -30.4000').fillna(False)
    payroll_data['Pay Description'] = np.where(cond, 'NORMAL', payroll_data['Pay Description'])


    OTE_paycodesBigBoats = paycode_mapping.loc[
            paycode_mapping['CLIENT MAP FOR SG'] == 'Y', 'Combined_PayCode'
        ].dropna().tolist()

    OTE_paycodesSW = paycode_mapping.loc[
            paycode_mapping['SW MAP'] == 'OTE', 'Combined_PayCode'
        ].dropna().tolist()

    SUPER_paycodesSW = paycode_mapping.loc[
            paycode_mapping['SW MAP'] == 'SUPER - SG', 'Combined_PayCode'
        ].dropna().tolist()

        # NOTE: use literal 'S&W' (not HTML-escaped)
    SnW_paycodesSW = paycode_mapping.loc[
            paycode_mapping['SW MAP'] == 'S&W', 'Combined_PayCode'
        ].dropna().tolist()

    Tax_paycodesSW = paycode_mapping.loc[
            paycode_mapping['SW MAP'] == 'TAX', 'Combined_PayCode'
        ].dropna().tolist()

        # ---- 4) Combined paycode in payroll data ----

        # Split at the first space; everything before -> 'Code_Prefix', after -> 'Code_Remainder'
    payroll_data[['Code_Prefix', 'Code_Remainder']] = (
            payroll_data['Code']
                .astype(str)
                .str.strip()
                .str.split(n=1, pat=' ', expand=True)
        )


    payroll_data['Line'] = payroll_data['Code_Prefix'].fillna('')

    payroll_data['Code'] = payroll_data['Code_Remainder'].fillna('')

    payroll_data = payroll_data.drop(columns=['Code_Prefix', 'Code_Remainder'])


    payroll_data['Combined_PayCode'] = (
            payroll_data['Code'].astype(str) 
            + '_' + payroll_data['Pay Description'].astype(str)
        )

    payroll_data['Combined_PayCode'] = payroll_data['Combined_PayCode'].str.upper().str.strip()

        # ---- 5) Mappings ----
    payroll_data['Client Mapping'] = np.where(
            payroll_data['Combined_PayCode'].isin(OTE_paycodesBigBoats), 'Y', 'N'
        )

    payroll_data['SW mapping'] = np.select(
            [
                payroll_data['Combined_PayCode'].isin(OTE_paycodesSW),
                payroll_data['Combined_PayCode'].isin(SnW_paycodesSW),
                payroll_data['Combined_PayCode'].isin(SUPER_paycodesSW),
                payroll_data['Combined_PayCode'].isin(Tax_paycodesSW),
            ],
            ['OTE', 'S&W', 'SUPER', 'TAX'],
            default='N/A'
        )

        # ---- 6) OTE buckets ----
    payroll_data['Client Map - OTE (not capped)'] = np.where(
            payroll_data['Combined_PayCode'].isin(OTE_paycodesBigBoats), payroll_data['Amount'], 0
        )

    payroll_data['SW Map - OTE (not capped)'] = np.where(
            payroll_data['Combined_PayCode'].isin(OTE_paycodesSW), payroll_data['Amount'], 0
        )

    payroll_data['SW Map - S&W (not capped)'] = np.where(
            payroll_data['Combined_PayCode'].isin(SnW_paycodesSW), payroll_data['Amount'], 0
        )

        # ---- 7) SG expected & actual ----
    payroll_data['Client Map - OTE SG (Not capped)'] = (
            payroll_data['Client Map - OTE (not capped)'] * payroll_data['SG_Rate']
        )
    # Remove round here to keep precision for later calculations
    #.round(2)

    payroll_data['SW Map - OTE SG (Not capped)'] = (
            payroll_data['SW Map - OTE (not capped)'] * payroll_data['SG_Rate']
        )
    # Remove round here to keep precision for later calculations
    #.round(2)

    payroll_data['SW Map - S&W SG (Not capped)'] = (
            payroll_data['SW Map - S&W (not capped)'] * payroll_data['SG_Rate']
        )
    # Remove round here to keep precision for later calculations
    #.round(2)

    payroll_data['Payroll - actual SG paid'] = np.where(
            payroll_data['Combined_PayCode'].isin(SUPER_paycodesSW), payroll_data['Amount'], 0
        )

    payroll_data['SCH - actual SG received'] = 0  # adjust when SCH data available

    payroll_data['OTE SG Expected - Client to SW Map Discrepancy'] = (
            payroll_data['Client Map - OTE SG (Not capped)'] - payroll_data['SW Map - OTE SG (Not capped)']
         )
    # Remove round here to keep precision for later calculations
    #.round(2)

        # ---- 8) IDs & output ----
    payroll_data['QtrEMPLID'] = payroll_data['Emp.Code'].astype(str) + '_' + payroll_data['FY_Q_Label']
       

    filename = f"payroll_data_{file_suffix}.csv"
    payroll_data.to_csv(filename, index=False)
    print(f"Saved to {filename}")

    return payroll_data



payroll_calc(Payroll_Labour_data, file_suffix="LABOUR")
payroll_calc(Payroll_Offshore_data, file_suffix="OFFSHORE")

mergedData_Labour = payroll_calc(Payroll_Labour_data, file_suffix="LABOUR")
mergedData_Offshore = payroll_calc(Payroll_Offshore_data, file_suffix="OFFSHORE")


print(mergedData_Labour.columns)


# # # # End of merge DataFrames for Labour and Offshore Payroll


# # # # Create QTR Results Table 


""" Key Business Assumptions


Grouping Logic

Each employee-quarter-paycode combination is treated as a unique record for compliance and reporting.



MCB Threshold

Uses fixed annual OTE caps per financial year to determine SG obligations.
Assumes these caps align with ATO superannuation guarantee rules.



Expected SG Calculation

SG is calculated at the financial year’s statutory rate.
Contributions are capped at MCB for high earners.
Assumes no other exceptions (e.g., age-based exemptions).



Mapping Integrity

Relies on accurate classification of pay codes into SW and Client mappings.
Discrepancy logic assumes mapping errors indicate potential compliance or billing issues.



Data Cleansing

Assumes upstream payroll data is already cleaned and validated before aggregation.



Discrepancy Commentary

Flags mismatches between Client and SW mappings as potential overpayment or underpayment risks.

 """
def aggregate_quarterly_data(df, output_dir="output", file_suffix="LABOUR"):
    """
    Aggregates payroll data by employee code, pay code, and fiscal quarter,
    then saves the output as a CSV file.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing payroll data.
    output_dir (str): Directory where the output CSV should be saved.
    file_suffix (str): Suffix to differentiate output files.

    Returns:
    pd.DataFrame: Aggregated quarterly payroll summary.
    """

    # Define aggregation methods
    agg_methods = {
        'Full_Name': 'first',  
        'Pay_Number': 'first',
        'Line': 'first',
        'Code': 'first',
        'Pay Description': 'first',
        'Hours/Value': 'sum',
        'Pay_Rate': 'mean',
        'Amount': 'sum',
        'SG_Rate': 'mean',
        'FY_Q': 'first',
        'Period_Ending': 'first',
        'Financial_Year': 'first', 
       'Client Mapping' : 'first',
        'SW mapping' : 'first',
        'Client Map - OTE (not capped)' : 'sum',
        'SW Map - OTE (not capped)' : 'sum',
        'SW Map - S&W (not capped)' : 'sum',
        'Client Map - OTE SG (Not capped)' : 'sum',
        'SW Map - OTE SG (Not capped)' : 'sum' , 
        'SW Map - S&W SG (Not capped)' : 'sum',
        'Payroll - actual SG paid' : 'sum', 
        'SCH - actual SG received' : 'sum'
    }

    # Ensure required columns exist in DataFrame before aggregating
    existing_columns = df.columns.intersection(agg_methods.keys())
    agg_methods = {col: agg_methods[col] for col in existing_columns}

    # Ensure the required group-by columns exist
    group_by_columns = ['QtrEMPLID', 'FY_Q_Label', 
                        'Emp.Code', 'Combined_PayCode', 'Unique_Key']
                #'Pay_Number']
   # #group_by_columns = ['QtrEMPLID', 'FY_Q_Label', 'Emp.Code', 'Pay_Number', 'Code']
    missing_cols = [col for col in group_by_columns if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Perform aggregation
    quarterly_summary = (
        df
        .groupby(group_by_columns)
        .agg(agg_methods)
        .reset_index()
    )
    
    quarterly_summary['Pay_Rate'] = quarterly_summary['Pay_Rate'].astype(float).round(2)


    
    # # # Step 2:  Add Column MCB

    quarterly_summary['MCB'] = np.where(
        quarterly_summary['Financial_Year'] == 2021, 57090, # Need to confirm with Paul or Ollie if this is correct
        np.where(
            quarterly_summary['Financial_Year'] == 2022, 58920,
            np.where(
                quarterly_summary['Financial_Year'] == 2023, 60220,
                np.where(quarterly_summary['Financial_Year']  == 2024, 62270, 
                         
              0)
            )
        )
    )

    # Add Column SW - Expected Minimum SG
    quarterly_summary['SW - Exepected Minimum SG'] = np.where(
    quarterly_summary['SW Map - OTE (not capped)'] > quarterly_summary['MCB'],
    quarterly_summary['MCB'] * quarterly_summary['SG_Rate'], np.where(
       quarterly_summary['SW Map - OTE (not capped)']  < quarterly_summary['MCB'], 
       quarterly_summary['SW Map - OTE (not capped)'] * quarterly_summary['SG_Rate'],
       0 
        )
    )
    # Round SW - Expected Minimum SG
    quarterly_summary['SW - Exepected Minimum SG'] = quarterly_summary['SW - Exepected Minimum SG'].astype(float).round(2)




    # Add Column Client - Expected Minimum SG

    quarterly_summary['Client - Exepected Minimum SG'] = np.where(
    quarterly_summary['Client Map - OTE (not capped)'] > quarterly_summary['MCB'],
    quarterly_summary['MCB'] * quarterly_summary['SG_Rate'], np.where(
       quarterly_summary['Client Map - OTE (not capped)']  < quarterly_summary['MCB'], 
       quarterly_summary['Client Map - OTE (not capped)'] * quarterly_summary['SG_Rate'],
       0 
        )
    )
    # Round Client - Expected Minimum SG
    quarterly_summary['Client - Exepected Minimum SG'] = quarterly_summary['Client - Exepected Minimum SG'].astype(float).round(2)




    
    

    # Add Column Above / Met cap in relation to MCB
    quarterly_summary['Above / Met cap'] = np.where(quarterly_summary['SW Map - OTE (not capped)'] > quarterly_summary['MCB'], 'Above / met cap', 
        np.where(quarterly_summary['SW Map - OTE (not capped)'] < quarterly_summary['MCB'], 'Below cap', "N/A"))
    


    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define output file path
    filename = os.path.join(output_dir, f"Quarterly_payroll_data_{file_suffix}.csv")

    # Save to CSV
    quarterly_summary.to_csv(filename, index=False)

    print(f"File saved: {filename}")
    return quarterly_summary


# store the quarterly summary dataframes for labour and offshore
quarterly_summary_LAB = aggregate_quarterly_data(mergedData_Labour)
quarterly_summary_LAB['Entity'] = 'LABOUR'
quarterly_summary_OFF = aggregate_quarterly_data(mergedData_Offshore, file_suffix="OFFSHORE")
quarterly_summary_OFF['Entity'] = 'OFFSHORE'

# Combine both dataframes
combined_quarterly_summary = pd.concat([quarterly_summary_OFF, quarterly_summary_LAB], ignore_index=True)



# Added Unique Key to Line  ID as sometimes Pay Number is missing
combined_quarterly_summary['Line_ID'] = combined_quarterly_summary['Pay_Number'].astype(str) + '_' + combined_quarterly_summary['Line'].astype(str) + '_' + combined_quarterly_summary['Unique_Key'].astype(str)



# Add column for Discrepancy 1 - SW Comment if not exists
if 'SW - Final Comment' not in combined_quarterly_summary.columns:
    combined_quarterly_summary['Discrepancy 1 - SW Comment'] = ''





# Function to generate comments based on conditions
def generate_comment(row):
    if row['SW mapping'] == 'OTE' and row['Client Mapping'] == 'N':
        return f"No payment under Client Mapping {row['Line_ID']} Pay Description: {row['Pay Description']}"
    
    
    elif row['Client Mapping'] == 'Y' and row['SW mapping'] != 'OTE':
        return f"Overpayment, SW Mapping didn't classify {row['Line_ID']} Pay Description: {row['Pay Description']} as OTE"
    
    else:
        return row.get('Discrepancy 1 - SW Comment', None)



    # Add column for Discrepancy 1 - SW Map Expected / Client Map
combined_quarterly_summary['Discrepancy 1 - SW Map Expected / Client Map'] = (combined_quarterly_summary['Client Map - OTE SG (Not capped)'] - combined_quarterly_summary['SW Map - OTE SG (Not capped)']).round(2)

# Round Discrepancy 1 - SW Map Expected / Client Map
combined_quarterly_summary['Discrepancy 1 - SW Map Expected / Client Map'] = combined_quarterly_summary['Discrepancy 1 - SW Map Expected / Client Map'].astype(float).round(2)

    # Add column for Discrepancy 2 - Client Map - Expected Amount SG

combined_quarterly_summary['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = (combined_quarterly_summary['Payroll - actual SG paid'] - combined_quarterly_summary['Client Map - OTE SG (Not capped)']).round(2)
    
combined_quarterly_summary['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = combined_quarterly_summary['Discrepancy 2 -  Client Map Expected / Payroll Paid'].astype(float).round(2)
# Add column for Discrepancy 3 - SW Map Expected / Payroll paid
combined_quarterly_summary['Discrepancy 3 - SW Map Expected / Payroll paid'] = (combined_quarterly_summary['Payroll - actual SG paid'] - combined_quarterly_summary['SW Map - OTE SG (Not capped)']).round(2)

combined_quarterly_summary['Discrepancy 3 - SW Map Expected / Payroll paid'] = combined_quarterly_summary['Discrepancy 3 - SW Map Expected / Payroll paid'].astype(float).round(2)

# Generate comments for Discrepancy 1 - SW Comment
combined_quarterly_summary['Discrepancy 1 - SW Comment'] = combined_quarterly_summary.apply(generate_comment, axis=1)


#Inital formula: 
combined_quarterly_summary['Discrepancy 1 - SW Comment'] = combined_quarterly_summary.apply(generate_comment, axis=1)




combined_quarterly_summary.to_csv('Payroll_Detail.csv', index=False)


# # # # # End of Create QTR Results Table







# # # # # Start of Create QTR Summary Table


""" Key Business Assumptions


Quarter-Level Reporting

Each employee-quarter combination is summarised into one record for easier compliance checks and client reporting.



Aggregation Logic

Totals for monetary values (e.g., SG, OTE).
Averages for rates (SG rate, pay rate).
First/last values for identifiers and descriptive fields.
Assumes these aggregation choices reflect business reporting needs.



Discrepancy Rules

If actual SG paid = 0, flag as “No Super paid”.
If expected SG (Client or SW) = 0, flag as mapping issue.
If expected SG ≠ actual SG, classify as underpayment or overpayment.
Assumes discrepancies indicate compliance or billing risks.



Comment Consolidation

Combines multiple pay-run level comments into a single quarter-level summary for clarity.
Assumes concatenated comments help auditors and managers quickly review anomalies.



Data Integrity

Relies on upstream data being clean and correctly mapped (e.g., OTE vs SG buckets).
Assumes SG rate and MCB logic applied earlier remain valid.
 """


# Need to create a dataframe that gets the Amount for quarter rather than the individual pay numbers
quarter_sum = combined_quarterly_summary

agg_methods = {\
        'Entity' : 'first',
        'Emp.Code' : 'first',
        'Full_Name': 'first',  
        'Pay_Number': 'last',
        'Unique_Key': 'last',
        'Hours/Value': 'sum',
        'Pay_Rate': 'mean',
        'Amount': 'sum',
        'SG_Rate': 'mean',
        'FY_Q': 'first',
        'Financial_Year': 'first', 
        'Client Map - OTE (not capped)': 'sum',
        'SW Map - OTE (not capped)': 'sum',
        'SW Map - S&W (not capped)': 'sum',
        'Client Map - OTE SG (Not capped)': 'sum',
        'SW Map - OTE SG (Not capped)': 'sum', 
        'SW Map - S&W SG (Not capped)': 'sum',
        'Payroll - actual SG paid': 'sum', 
        'SCH - actual SG received': 'sum',
        'MCB' : 'first'
      

    }






# Check if required columns exist in DataFrame
group_by_columns = ['QtrEMPLID', 'Period_Ending']
missing_cols = [col for col in group_by_columns if col not in quarter_sum.columns]

if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Perform aggregation
quarter_sum = quarter_sum.groupby(group_by_columns).agg(agg_methods).reset_index()


quarter_sum['Pay_Rate'] = quarter_sum['Pay_Rate'].astype(float).round(2)


# Group by 'Pay_Number' and concatenate 'Discrepancy 1 - SW Comment' values
comment_concat = (
    combined_quarterly_summary
    .groupby('Unique_Key')['Discrepancy 1 - SW Comment']
    .apply(lambda x: ' | '.join(x.dropna().astype(str)))
    .reset_index()
)



# Merge the concatenated comment back correctly
quarter_sum = quarter_sum.merge(comment_concat, on='Unique_Key', how='left')




def generate_comment1(row):
    if row['Payroll - actual SG paid'] == 0:
        #return f"No Super was paid under pay run number: {row['Pay_Number']}"
        return f"No Super was paid under pay run unique key: {row['Unique_Key']}"
    elif row['Client Map - OTE SG (Not capped)'] == 0:
        #return f"Client Mapping didn't make payment under pay run number: {row['Pay_Number']}"
        return f"Client Mapping didn't make payment under pay run unique key: {row['Unique_Key']}"
    # Adde 4/06/2025 as per OM advise
    elif row['Client Map - OTE SG (Not capped)'] != row['Payroll - actual SG paid']:
        return f"Underpayment within pay unique key: {row['Unique_Key']}" if row['Client Map - OTE SG (Not capped)'] > row['Payroll - actual SG paid'] else f"Overpayment under pay unique key: {row['Unique_Key']}"
    else:
        return row.get('Discrepancy 2 - SW Comment', '')



def generate_comment2(row):
    
    if row['Payroll - actual SG paid'] == 0:
        
        return f"No Super was paid under pay unique key: {row['Unique_Key']}"
    elif row['SW Map - OTE SG (Not capped)'] == 0:
        
        return f"SW Mapping didn't make payment under pay unique key: {row['Unique_Key']}"
        
    
    else:
        return row.get('Discrepancy 3 - SW Comment', '')



quarter_sum['Discrepancy 2 - SW Comment'] = quarter_sum.apply(generate_comment1, axis=1)
quarter_sum['Discrepancy 3 - SW Comment'] = quarter_sum.apply(generate_comment2, axis=1)



quarter_sum.to_csv('Quarterly_Sum.csv', index=False)

 # # # # # End of Create QTR Summary Table



# # # # # Start of Create SG Actual vs SW Map Summary Table
""" Key Business Assumptions


Quarter-level reconciliation

QtrEMPLID uniquely represents employee + financial quarter; aggregation is performed only at this grain for compliance reporting.



MCB (Minimum Contribution Benchmark) as cap basis

OTE for SG purposes is capped at MCB when OTE exceeds it.
Expected SG is therefore calculated against the capped OTE in final reconciliation, reflecting ATO SG cap practice for high earners.



Expected vs Actual logic

Expected SG (Client vs SW) is derived from OTE buckets and the statutory SG rate for the year.
Actual SG paid comes from payroll and is the source of truth for payment.
The three discrepancies (Client vs SW expectations; actual vs each expectation) are primary signals for:

Misclassification of pay codes (mapping issues),
Payroll under/overpayments,
Combined classification/payment problems.





Materiality threshold

Discrepancies within ±$0.08 are considered immaterial, reducing noise in audit reviews.



Tolerance in diagnostic matching

Uses numeric tolerance (0.07 / 0.03) to identify near‑equal relationships between discrepancies; this acknowledges rounding and minor variances in SG computation across systems.



Comment consolidation

Quarter‑level commentary aggregates all underlying pay‑run comments so reviewers have context in a single row; assumes quarter_sum is correctly prepared.
 """


def SG_actual_Vs_SW_Map(df, output_dir="output"):
    # Define aggregation methods
    agg_methods = {\
        'Entity' : 'first',
        'Emp.Code' : 'first',
        'Full_Name': 'first',  
        'Pay_Number': 'first',
        'Unique_Key': 'first',
        'Hours/Value': 'sum',
        'Pay_Rate': 'mean',
        'Amount': 'sum',
        'SG_Rate': 'mean',
        'FY_Q': 'first',
        'Financial_Year': 'first', 
        'Client Map - OTE (not capped)': 'sum',
        'SW Map - OTE (not capped)': 'sum',
        'SW Map - S&W (not capped)': 'sum',
        'Client Map - OTE SG (Not capped)': 'sum',
        'SW Map - OTE SG (Not capped)': 'sum', 
        'SW Map - S&W SG (Not capped)': 'sum',
        'Payroll - actual SG paid': 'sum', 
        'SCH - actual SG received': 'sum',
        'MCB' : 'first'
    }


    

    # Check if required columns exist in DataFrame
    group_by_columns = ['QtrEMPLID']
    missing_cols = [col for col in group_by_columns if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Perform aggregation
    grouped_df = df.groupby(group_by_columns).agg(agg_methods).reset_index()



    comment_concat = (
        quarter_sum
        .groupby('QtrEMPLID')['Discrepancy 1 - SW Comment']
        .apply(lambda x: ' | '.join(x.dropna().astype(str)))   
        .reset_index()

    )


        # Group by 'Pay_Number' and concatenate 'Discrepancy 1 - SW Comment' values
    comment_concat1 = (
        quarter_sum
        .groupby('QtrEMPLID')['Discrepancy 2 - SW Comment']
        .apply(lambda x: ' | '.join(x.dropna().astype(str)))
        .reset_index()
    )

    comment_concat2 = (
        quarter_sum
        .groupby('QtrEMPLID')['Discrepancy 3 - SW Comment']
        .apply(lambda x: ' | '.join(x.dropna().astype(str)))
        .reset_index()
    )


    # Merge the concatenated comment back correctly
    grouped_df = grouped_df.merge(comment_concat, on='QtrEMPLID', how='left')

    grouped_df = grouped_df.merge(comment_concat1, on='QtrEMPLID', how='left')

    grouped_df = grouped_df.merge(comment_concat2, on='QtrEMPLID', how='left')

    columns_to_drop = ['Pay_Number', 'Line', 'Hours/Value', 'Pay_Rate', 'Pay Description', 'Amount', 'Unique_Key']
     # Drop unneeded columns if provided
   
    

    grouped_df['OTE Client up to MCB'] = np.where(
        grouped_df['Client Map - OTE (not capped)'] > grouped_df['MCB'],
        grouped_df['MCB'], 
        grouped_df['Client Map - OTE (not capped)']
          )
    
    grouped_df['OTE SW up to MCB'] = np.where(
        grouped_df['SW Map - OTE (not capped)'] > grouped_df['MCB'],
        grouped_df['MCB'], 
        grouped_df['SW Map - OTE (not capped)']
    )


    # Add second column for Client so there will be one sw and one client Above / Met Cap
    grouped_df['Above / Met cap (SW Map)'] = np.where(grouped_df['SW Map - OTE (not capped)'] > grouped_df['MCB'], 'Above / met cap', 
        np.where(grouped_df['SW Map - OTE (not capped)'] < grouped_df['MCB'], 'Below cap', "N/A"))
    
    
    grouped_df['Above / Met cap (Client Map)'] = np.where(grouped_df['Client Map - OTE (not capped)'] > grouped_df['MCB'], 'Above / met cap',
        np.where(grouped_df['Client Map - OTE (not capped)'] < grouped_df['MCB'], 'Below cap', "N/A"))
    

    grouped_df["SG on Client OTE up to MCB"] = grouped_df['OTE Client up to MCB']  * grouped_df['SG_Rate']
    
    grouped_df["SG on SW OTE up to MCB"] = grouped_df['OTE SW up to MCB']  * grouped_df['SG_Rate']
    
    

    # Add column for Discrepancy 1 - SW Map Expected / Client Map
    grouped_df['Discrepancy 1 - SW Map Expected / Client Map'] = (grouped_df['Client Map - OTE SG (Not capped)'] - grouped_df['SW Map - OTE SG (Not capped)']).round(2)

    # Add column for Discrepancy 2 - Client Map - Expected Total SG

    grouped_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = (grouped_df['Payroll - actual SG paid'] - grouped_df['Client Map - OTE SG (Not capped)']).round(2)
    
    # Add column for Discrepancy 3 - SW Map Expected / Payroll paid
    grouped_df['Discrepancy 3 - SW Map Expected / Payroll paid'] = (grouped_df['Payroll - actual SG paid'] - grouped_df['SW Map - OTE SG (Not capped)']).round(2)
    
  

      

    def generate_comment_Discrep_3(row):
        disc1 = row['Discrepancy 1 - SW Map Expected / Client Map']
        disc2 = row['Discrepancy 2 -  Client Map Expected / Payroll Paid']
        disc3 = row['Discrepancy 3 - SW Map Expected / Payroll paid']

        if np.isclose(disc1, disc3, atol=0.07):
           # return f"Mapping issue with pay run: {row['Pay_Number']}"
            return f"Mapping issue with pay run: {row['Unique_Key']} "

        elif np.isclose(disc2, disc3, atol=0.07):
            return f"Refer to Discrepancy 2 - Client Map Expected / Payroll Paid for more details. Pay run: {row['Unique_Key']} "

        elif np.isclose(disc3, disc1 + disc2, atol=0.03):
            return f"Mapping and Payroll issue with pay run: {row['Unique_Key']} refer to Discrepancy 1 and 2 for more details"

        else:
            return f"Unknown issue with pay run: {row['Unique_Key']}"


    
    grouped_df['Discrepancy 3 - SW Comment'] = grouped_df.apply(generate_comment_Discrep_3, axis=1)

    
    # Added 4/06/2025 as per OM advise

    grouped_df['Discrepancy 3 - SW Comment'] = np.where(
        np.isclose(
            grouped_df['Discrepancy 3 - SW Map Expected / Payroll paid'],
            grouped_df['Discrepancy 1 - SW Map Expected / Client Map'],
            atol=0.07
        ),
        "Refer to Discrepancy 1",
        grouped_df['Discrepancy 3 - SW Comment']
    )


    grouped_df = grouped_df.drop(columns=columns_to_drop, errors='ignore')  # ignore errors if columns don't exist

    column_order = ['Entity', 'QtrEMPLID', 'Emp.Code', 'Full_Name', 'SG_Rate', 'FY_Q',
       'Financial_Year', 'Client Map - OTE (not capped)', 'SW Map - OTE (not capped)',
       'SW Map - S&W (not capped)', 'Client Map - OTE SG (Not capped)',
       'SW Map - OTE SG (Not capped)', 'SW Map - S&W SG (Not capped)',
       'MCB',
       'Payroll - actual SG paid', 
        'Discrepancy 1 - SW Map Expected / Client Map',
       'Discrepancy 2 -  Client Map Expected / Payroll Paid',
       'Discrepancy 3 - SW Map Expected / Payroll paid',
       'Discrepancy 1 - SW Comment', 'Discrepancy 2 - SW Comment',
       'Discrepancy 3 - SW Comment']

        
    # Reorder the DataFrame columns
    grouped_df = grouped_df[column_order]




  
   
    grouped_df['SG Paid => SG up to cap'] = np.where(
        grouped_df['Payroll - actual SG paid'] < (grouped_df['MCB'] * grouped_df['SG_Rate']), 'Below Cap',
        np.where(grouped_df['Payroll - actual SG paid'] > (grouped_df['MCB'] * grouped_df['SG_Rate']), 'Above Cap', 'Cap Met')
    )

    grouped_df['Client Map - OTE SG (Capped to MCB)'] = np.where(
        grouped_df['Client Map - OTE (not capped)'] == (grouped_df['MCB']), grouped_df['MCB'] * grouped_df['SG_Rate'],
        np.where(
            grouped_df['Client Map - OTE (not capped)'] > (grouped_df['MCB']),
            grouped_df['MCB'] * grouped_df['SG_Rate'],
            grouped_df['Client Map - OTE (not capped)'] * grouped_df['SG_Rate'] 
        )
       
    )


    grouped_df['SW Map - OTE SG (Capped to MCB)'] = np.where(
    grouped_df['SW Map - OTE (not capped)'] > grouped_df['MCB'],
    grouped_df['MCB'] * grouped_df['SG_Rate'],
    grouped_df['SW Map - OTE (not capped)'] * grouped_df['SG_Rate']
)

    



    grouped_df['Discrepancy 1 - SW Map Expected / Client Map'] = (grouped_df['Client Map - OTE SG (Capped to MCB)'] - grouped_df['SW Map - OTE SG (Capped to MCB)']).round(2)

    grouped_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = (grouped_df['Payroll - actual SG paid'] - grouped_df['Client Map - OTE SG (Capped to MCB)']).round(2)
    

    grouped_df['Discrepancy 3 - SW Map Expected / Payroll paid'] = (grouped_df['Payroll - actual SG paid'] - grouped_df['SW Map - OTE SG (Capped to MCB)']).round(2)





    print(grouped_df['Discrepancy 1 - SW Map Expected / Client Map'].dtype)
    print(grouped_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'].dtype)
    print(grouped_df['Discrepancy 3 - SW Map Expected / Payroll paid'].dtype)


    grouped_df['Discrepancy 1 - SW Map Expected / Client Map'] = pd.to_numeric(
        grouped_df['Discrepancy 1 - SW Map Expected / Client Map'], errors='coerce'
    )
    grouped_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = pd.to_numeric(
        grouped_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'], errors='coerce'
    )
    grouped_df['Discrepancy 3 - SW Map Expected / Payroll paid'] = pd.to_numeric(
        grouped_df['Discrepancy 3 - SW Map Expected / Payroll paid'], errors='coerce'
    )

    
    

    mask = (
        (grouped_df['Discrepancy 1 - SW Map Expected / Client Map'] > -0.08) &
        (grouped_df['Discrepancy 1 - SW Map Expected / Client Map'] < 0.08)
    )


    
    grouped_df.loc[mask, 'Discrepancy 1 - SW Comment'] = "No Discrepancy / Immaterial"
 

    
    mask1 = (
        (grouped_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'] > -0.08) &
        (grouped_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'] < 0.08)
    )

    grouped_df.loc[mask1, 'Discrepancy 2 - SW Comment'] = "No Discrepancy / Immaterial"

    mask2 = (
        (grouped_df['Discrepancy 3 - SW Map Expected / Payroll paid'] > -0.08) &
        (grouped_df['Discrepancy 3 - SW Map Expected / Payroll paid'] < 0.08)
    )

    grouped_df.loc[mask2, 'Discrepancy 3 - SW Comment'] = "No Discrepancy / Immaterial"


   
   



    def clean_discrepancy_comment(text):
        if not isinstance(text, str):
            return text
        text = re.sub(r'\|\s*\|', '', text)       # remove empty pipe fields
        text = re.sub(r'\|{2,}', '|', text)       # collapse multiple pipes
        return text.strip(' |')                   # trim leading/trailing pipes/spaces

    # Apply to grouped_df
    grouped_df['Discrepancy 1 - SW Comment'] = grouped_df['Discrepancy 1 - SW Comment'].apply(clean_discrepancy_comment)
    grouped_df['Discrepancy 2 - SW Comment'] = grouped_df['Discrepancy 2 - SW Comment'].apply(clean_discrepancy_comment)
    grouped_df['Discrepancy 3 - SW Comment'] = grouped_df['Discrepancy 3 - SW Comment'].apply(clean_discrepancy_comment)




    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define output file path
    #filename = os.path.join(output_dir, f"SG_actual_Vs_SW_Map_{file_suffix}.csv")
    filename = os.path.join(output_dir, f"SG_Quarterly_Combined.csv")
    # Save to CSV
    grouped_df.to_csv(filename, index=False)


    column_order = ['Entity', 'QtrEMPLID', 'Emp.Code', 'Full_Name', 'SG_Rate', 'FY_Q',
       'Financial_Year', 'Client Map - OTE (not capped)', 'SW Map - OTE (not capped)',
       'SW Map - S&W (not capped)', 'Client Map - OTE SG (Not capped)',
       'SW Map - OTE SG (Not capped)', 'SW Map - S&W SG (Not capped)',
       'MCB',
       'Client Map - OTE SG (Capped to MCB)',
       'SW Map - OTE SG (Capped to MCB)',
       'Payroll - actual SG paid', 
       'SG Paid => SG up to cap',
        'Discrepancy 1 - SW Map Expected / Client Map',
       'Discrepancy 2 -  Client Map Expected / Payroll Paid',
       'Discrepancy 3 - SW Map Expected / Payroll paid',
       'Discrepancy 1 - SW Comment', 'Discrepancy 2 - SW Comment',
       'Discrepancy 3 - SW Comment']
    
    grouped_df = grouped_df[column_order]

    print(f"File saved: {filename}")
    return grouped_df







output_dir="output"
combined_result_df = SG_actual_Vs_SW_Map(quarter_sum)

print(combined_result_df.columns)






filename = os.path.join(output_dir, f"SG_Quarterly_BothEntities.csv")
combined_result_df.to_csv(filename, index=False)




dataframes = [combined_result_df, quarter_sum, combined_quarterly_summary]

combined_result_df.to_csv('combined_result_with_comments.csv', index=False)




sheet_names = ['Qtr_Discrepancy_Results', 'Pay_Number_Summary', 'Payroll Detail']


output_excel = 'client_payroll_analysis.xlsx'


# Write each DataFrame to a separate sheet
with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
    for df, sheet_name in zip(dataframes, sheet_names):
        df.to_excel(writer, sheet_name=sheet_name, index=False)



### End of Create SG Actual vs SW Map Summary Table

