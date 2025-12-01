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


# File paths as of 19/11/2025
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


# Generate DataFrames
Payroll_Labour_data = process_payroll_data(Payroll_Labour_filepath)
Payroll_Offshore_data = process_payroll_data(Payroll_Offshore_filepath)

Super_Labour_data = process_super_data(Super_Labour_filepath)
Super_Offshore = process_super_data(Super_Offshore_filepath)



def payroll_calc(Payroll_Labour_data, file_suffix="LABOUR / OFFSHORE"):
    """
    Process payroll data, map paycodes to OTE/S&W/SUPER/TAX, compute SG expected & actual,
    and save a CSV. Returns the processed DataFrame.
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

    payroll_data['FY_Q'] = np.where(
        month.isin([7, 8, 9]), 'Q1',
        np.where(
            month.isin([10, 11, 12]), 'Q2',
            np.where(
                month.isin([1, 2, 3]), 'Q3',
                np.where(month.isin([4, 5, 6]), 'Q4', 'Unknown')
            )
        )
    )

    # FY: months Jul–Dec belong to the *next* FY; Jan–Jun belong to the current FY
    payroll_data['Financial_Year'] = np.where(
        month >= 7,
        payroll_data['Period_Ending'].dt.year + 1,
        payroll_data['Period_Ending'].dt.year
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
        'ACKNOWLEDGEMENT'

            ]



    payroll_data = payroll_data[~payroll_data['Pay Description'].isin(drop_names)]

    
    cond = payroll_data['Pay Description'].eq('NORMAL -30.4000').fillna(False)
    payroll_data['Pay Description'] = np.where(cond, 'NORMAL', payroll_data['Pay Description'])


 
    paycode_mapping['Combined_PayCode'] = (
            paycode_mapping['PayCode'].astype(str) + '_' + paycode_mapping['Description'].astype(str)
        )

        # Lists
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
        ).round(2)

    payroll_data['SW Map - OTE SG (Not capped)'] = (
            payroll_data['SW Map - OTE (not capped)'] * payroll_data['SG_Rate']
        ).round(2)

    payroll_data['SW Map - S&W SG (Not capped)'] = (
            payroll_data['SW Map - S&W (not capped)'] * payroll_data['SG_Rate']
        ).round(2)

    payroll_data['Payroll - actual SG paid'] = np.where(
            payroll_data['Combined_PayCode'].isin(SUPER_paycodesSW), payroll_data['Amount'], 0
        )

    payroll_data['SCH - actual SG received'] = 0  # adjust when SCH data available

    payroll_data['OTE SG Expected - Client to SW Map Discrepancy'] = (
            payroll_data['Client Map - OTE SG (Not capped)'] - payroll_data['SW Map - OTE SG (Not capped)']
        ).round(2)

        # ---- 8) IDs & output ----
    payroll_data['QtrEMPLID'] = payroll_data['Emp.Code'].astype(str) + '_' + payroll_data['FY_Q_Label']
        #payroll_data['QtrEMPLID'] = payroll_data['Full_Name'].astype(str) + '_' + payroll_data['FY_Q_Label']

        # # Optional: rename to tidy if you had Description_x
        # if desc_col == 'Description_x':
        #     payroll_data = payroll_data.rename(columns={'Description_x': 'Description'})

        # Save to CSV with dynamic suffix
    filename = f"payroll_data_{file_suffix}.csv"
    payroll_data.to_csv(filename, index=False)
    print(f"Saved to {filename}")

    return payroll_data



payroll_calc(Payroll_Labour_data, file_suffix="LABOUR")
payroll_calc(Payroll_Offshore_data, file_suffix="OFFSHORE")

mergedData_Labour = payroll_calc(Payroll_Labour_data, file_suffix="LABOUR")
mergedData_Offshore = payroll_calc(Payroll_Offshore_data, file_suffix="OFFSHORE")


print(mergedData_Labour.columns)



# def calculate_shortfall_offset(mergedData_Labour):
#     agg_methods = {
#         'Full_Name': 'first',  
#         'Line': 'first',
#         'Description': 'first',
#         'Hours/Value': 'sum',
#         'Pay_Rate': 'mean',
#         'Total': 'sum',
#         'SG_Rate': 'mean',
#         'FY_Q': 'first',
#         'Financial_Year': 'first', 
#         'Client Mapping': 'first',
#         'SW mapping': 'first',
#         'Client Map - OTE (not capped)': 'sum',
#         'SW Map - OTE (not capped)': 'sum',
#         'SW Map - S&W (not capped)': 'sum',
#         'Client Map - OTE SG (Not capped)': 'sum',
#         'SW Map - OTE SG (Not capped)': 'sum', 
#         'SW Map - S&W SG (Not capped)': 'sum',
#         'Payroll - actual SG paid': 'sum', 
#         'SCH - actual SG received': 'sum'
#     }


#     df1 = mergedData_Labour.groupby(['Period_Ending', 'Pay_Number', 'Emp.Code']).agg(agg_methods).reset_index()
#     df1 = df1.sort_values(by=['Emp.Code', 'Period_Ending'])

#     df1['Pay_Rate'] = df1['Pay_Rate'].astype(float).round(2)

#     df1['SW Map - OTE SG (Not capped)'] = df1['SW Map - OTE SG (Not capped)'].round(2)
#     df1['Shortfall SG'] = df1['Payroll - actual SG paid'] - df1['SW Map - OTE SG (Not capped)']
#     df1['clumative_sum'] = df1.groupby(['Emp.Code'])['Shortfall SG'].cumsum()

#     df1 = df1.sort_values(by=['Emp.Code', 'Period_Ending'])

#     df1['cumulative_sum_12Months_OVERPAY'] = df1.groupby('Emp.Code').apply(
#         lambda g: g.apply(
#             lambda row: g.loc[
#                 (g['Period_Ending'] > row['Period_Ending'] - pd.DateOffset(years=1)) &
#                 (g['Period_Ending'] <= row['Period_Ending']) &
#                 (g['Shortfall SG'] > 0.01),
#                 'Shortfall SG'
#             ].sum(), axis=1)
#     ).reset_index(level=0, drop=True)

#     df1['Adjust_shortfall_Y/N'] = np.where(
#         (df1['Shortfall SG'] < 0) & (df1['cumulative_sum_12Months_OVERPAY'] > 0), 'Y', 'N'
#     )

#     df1['cumulative_sum_12Months'] = df1.groupby('Emp.Code').apply(
#         lambda g: g.apply(
#             lambda row: g.loc[
#                 (g['Period_Ending'] > row['Period_Ending'] - pd.DateOffset(years=1)) &
#                 (g['Period_Ending'] <= row['Period_Ending']) &
#                 (g['Adjust_shortfall_Y/N'] == 'Y'),
#                 'Shortfall SG'
#             ].sum(), axis=1)
#     ).reset_index(level=0, drop=True)

#     df1['Available_Balance'] = np.where(
#         df1['Adjust_shortfall_Y/N'] == 'Y', 
#         df1['cumulative_sum_12Months_OVERPAY'] + df1['cumulative_sum_12Months'],
#         np.nan
#     )

#     df1['Offset_Shortfall_Y/N'] = np.where(
#         (df1['Shortfall SG'] < 0) & (df1['Available_Balance'] > abs(df1['Shortfall SG'])), 'Y',
#         np.where(
#             (df1['Shortfall SG'] < 0) & (df1['cumulative_sum_12Months_OVERPAY'] > 0) & 
#             (abs(df1['Available_Balance']) < abs(df1['Shortfall SG'])), 'P',
#             'N'
#         )
#     )

#     df1['Shortfall_Reduction'] = np.where(
#         df1['Offset_Shortfall_Y/N'] == 'Y',
#         df1['Shortfall SG'],
#         np.where(df1['Offset_Shortfall_Y/N'] == 'P', 
#                  -(abs(df1['Shortfall SG']) - abs(df1['Available_Balance'])),
#                  np.where(df1['Offset_Shortfall_Y/N'] == 'N', 0, 0))
#     )

#     df1['Remaining_Shortfall_Balance'] = np.where(
#         ((df1['Available_Balance'] <= 0) & (df1['Offset_Shortfall_Y/N'] == 'N')), df1['Shortfall SG'],
#         np.where(
#             ((df1['Available_Balance'] <= 0) & (df1['Offset_Shortfall_Y/N'] == 'P')), df1['Available_Balance'],
#             np.where(
#                 ((df1['Offset_Shortfall_Y/N'] == 'N') & (df1['Shortfall SG'] < 0)), df1['Shortfall SG'],
#                 0
#             )
#         )
#     )

#     df1['One_Year_Prior'] = df1['Period_Ending'] - pd.DateOffset(years=1)

#     return df1

# offset = calculate_shortfall_offset(mergedData_Labour)
# offset.to_csv('RollingShortfallOffset_output.csv', index=False)

# Commented out to test the new function
# agg_methods = {
#         'Full_Name': 'first',  
#         'Line': 'first',
#         'Description': 'first',
#         'Hours/Value': 'sum',
#         'Pay_Rate': 'mean',
#         'Total': 'sum',
#         'SG_Rate': 'mean',
#         'FY_Q': 'first',
#         'Financial_Year': 'first', 
#        'Client Mapping' : 'first',
#         'SW mapping' : 'first',
#         'Client Map - OTE (not capped)' : 'sum',
#         'SW Map - OTE (not capped)' : 'sum',
#         'SW Map - S&W (not capped)' : 'sum',
#         'Client Map - OTE SG (Not capped)' : 'sum',
#         'SW Map - OTE SG (Not capped)' : 'sum' , 
#         'SW Map - S&W SG (Not capped)' : 'sum',
#         'Payroll - actual SG paid' : 'sum', 
#         'SCH - actual SG received' : 'sum'
#     }



# # # # Create QTR Results Table 

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
        #'Unique_Key': 'first',
        'Line': 'first',
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


     # Drop unneeded columns if provided
   
    #quarterly_summary = quarterly_summary.drop(columns=columns_to_drop, errors='ignore')  # ignore errors if columns don't exist

    
    # # # Step 2:  Add Column MCB
    # 2020 - 2021 - $57 090

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



    # Where Paycode is in list 1 & is not in list 2
    # Return Y
    # If not return N

    # Add two code blocks now for the same but Y or N


    quarterly_summary['SW - Exepected Minimum SG'] = np.where(
    quarterly_summary['SW Map - OTE (not capped)'] > quarterly_summary['MCB'],
    quarterly_summary['MCB'] * quarterly_summary['SG_Rate'], np.where(
       quarterly_summary['SW Map - OTE (not capped)']  < quarterly_summary['MCB'], 
       quarterly_summary['SW Map - OTE (not capped)'] * quarterly_summary['SG_Rate'],
       0 
        )
    )

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

    quarterly_summary['Client - Exepected Minimum SG'] = quarterly_summary['Client - Exepected Minimum SG'].astype(float).round(2)




    
    


    quarterly_summary['Above / Met cap'] = np.where(quarterly_summary['SW Map - OTE (not capped)'] > quarterly_summary['MCB'], 'Above / met cap', 
        np.where(quarterly_summary['SW Map - OTE (not capped)'] < quarterly_summary['MCB'], 'Below cap', "N/A"))
    

    # commented out 27/06/2025

    # quarterly_summary['Payroll - actual SG paid_CumSum'] = quarterly_summary.groupby(['Pay_Number'])['Payroll - actual SG paid'].cumsum()

    # quarterly_summary['Client Mapping - OTE SG Expected_CumSum'] = quarterly_summary.groupby(['Pay_Number'])['Client Map - OTE SG (Not capped)'].cumsum()

    # quarterly_summary['SW Map - OTE SG expected_CumSum'] = quarterly_summary.groupby(['Pay_Number'])['SW Map - OTE SG (Not capped)'].cumsum()



    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define output file path
    filename = os.path.join(output_dir, f"Quarterly_payroll_data_{file_suffix}.csv")

    # Save to CSV
    quarterly_summary.to_csv(filename, index=False)

    print(f"File saved: {filename}")
    return quarterly_summary



quarterly_summary_LAB = aggregate_quarterly_data(mergedData_Labour)
quarterly_summary_LAB['Entity'] = 'LABOUR'
quarterly_summary_OFF = aggregate_quarterly_data(mergedData_Offshore, file_suffix="OFFSHORE")
quarterly_summary_OFF['Entity'] = 'OFFSHORE'

combined_quarterly_summary = pd.concat([quarterly_summary_OFF, quarterly_summary_LAB], ignore_index=True)



# Added Unique Key to Line  ID as sometimes Pay Number is missing
combined_quarterly_summary['Line_ID'] = combined_quarterly_summary['Pay_Number'].astype(str) + '_' + combined_quarterly_summary['Line'].astype(str) + '_' + combined_quarterly_summary['Unique_Key'].astype(str)


# Paycode summary 
# Test 27/06/2025
#paycode_summary = combined_quarterly_summary




paycode_summary = combined_quarterly_summary.copy()

paycode_summary['FY_Q_Label'] = paycode_summary['Financial_Year'].astype(str) + '_' + paycode_summary['FY_Q']

paycode_summary['PayCode'] = paycode_summary['Combined_PayCode'].str.split('_').str[0]


paycode_summary.groupby(['Combined_PayCode', 'Pay Description','Period_Ending']).agg({
    'Client Map - OTE (not capped)': 'sum',
    'SW Map - OTE (not capped)': 'sum',
    'SW Map - S&W (not capped)': 'sum',
    'Client Map - OTE SG (Not capped)': 'sum',
    'SW Map - OTE SG (Not capped)': 'sum',
    'SW Map - S&W SG (Not capped)': 'sum',
    'Payroll - actual SG paid': 'sum',
    'SCH - actual SG received': 'sum',
    'Amount': 'sum'
}).reset_index()

# paycode_list = [
#    '8',
# '9',
# 'AL',
# 'AL-CASHO',
# 'BACK',
# 'BEREAVE',
# 'BONUS',
# 'BPAY',
# 'CASBNS',
# 'CBUS',
# 'CHILD',
# 'EXTRA',
# 'HRSBNS',
# 'LOAD',
# 'LOADING',
# 'LSL',
# 'MVGARTH',
# 'NORMAL',
# 'ORD',
# 'OT1.5',
# 'OT2.0',
# 'OT2.5',
# 'PH',
# 'PL-VACC',
# 'SL',
# 'TAFE',
# 'VEHICLE',
# 'WCOMP',
# 'WCOMP-EX',
# 'WORK-EX2',
# 'WRIL',
# 'WRKDJ'
 
# ]

Super = [
    '8',
'9',
'CBUS',
'SUPER'
]


Taxable_Wages = [
'AL',
'AL-CASHO',
'BACK',
'BEREAVE',
'BONUS',
'BPAY',
'CASBNS',
'EXTRA',
'FLEXI',
'HRSBNS',
'LOAD',
'LOADING',
'LSL',
'NORMAL',
'ORD',
'OT1.5',
'OT2.0',
'OT2.5',
'PH',
'PL-VACC',
'SL',
'TAFE',
'WCOMP-EX',
'WCOMP'
]


SALSAC_list = [
    'SACRIFIC',
'SALSAC',
'SS',
'SS JC',
'SS JN'
]

CHILD_list = [
    'CHILD'
]


TAX_list = [
    'NORMTAX',
'VOLTAX'
]



#paycode_summary = paycode_summary[paycode_summary['PayCode'].isin(paycode_list)]

paycode_summary['Payroll Tax - Eligible'] = np.where(
    paycode_summary['PayCode'].isin(Taxable_Wages), paycode_summary['Amount'], 0
)

paycode_summary['Super - Eligible'] = np.where(
    paycode_summary['PayCode'].isin(Super), paycode_summary['Amount'], 0
)

paycode_summary['SALSAC - Eligible'] = np.where(
    paycode_summary['PayCode'].isin(SALSAC_list), paycode_summary['Amount'], 0
)
paycode_summary['Child - Eligible'] = np.where(
    paycode_summary['PayCode'].isin(CHILD_list), paycode_summary['Amount'], 0
)

paycode_summary['Tax - Eligible'] = np.where(
    paycode_summary['PayCode'].isin(TAX_list), paycode_summary['Amount'], 0
)

print('Period Ending Data Type')
print(paycode_summary['Period_Ending'].dtype)


paycode_summary['Period_Ending'] = pd.to_datetime(paycode_summary['Period_Ending'], errors='coerce')

paycode_summary['Month'] = paycode_summary['Period_Ending'].dt.month




paycode_summary['Financial_Year'] = paycode_summary['Financial_Year'].astype(str)
print(paycode_summary['Financial_Year'].dtype)
#paycode_summary = paycode_summary[paycode_summary['Financial_Year'] == '2024']




paycode_summary.to_csv('Paycode_Summary_new_input_file_fullFYs.csv', index=False)



if 'SW - Final Comment' not in combined_quarterly_summary.columns:
    combined_quarterly_summary['Discrepancy 1 - SW Comment'] = ''




# def generate_comment(row):
#     if row['Client Mapping - OTE SG Expected'] == 0:
    
#         #return f"Client Mapping didn't make payment under this line {row['Line_ID']} Description: {row['Description']}"
#         return f"Client Mapping didn't classify line: {row['Line_ID']} as OTE"
#     elif row['SW Map - OTE SG (Not capped)'] == 0:
#         return f"SW Mapping didn't classify line: {row['Line_ID']} as OTE"
#     else:
#         return row.get('Discrepancy 1 - SW Comment', '')

def generate_comment(row):
    if row['SW mapping'] == 'OTE' and row['Client Mapping'] == 'N':
        return f"No payment under Client Mapping {row['Line_ID']} Pay Description: {row['Pay Description']}"
    
    
    elif row['Client Mapping'] == 'Y' and row['SW mapping'] != 'OTE':
        return f"Overpayment, SW Mapping didn't classify {row['Line_ID']} Pay Description: {row['Pay Description']} as OTE"
    
    else:
        return row.get('Discrepancy 1 - SW Comment', None)



    # Add column for Discrepancy 1 - SW Map Expected / Client Map
combined_quarterly_summary['Discrepancy 1 - SW Map Expected / Client Map'] = (combined_quarterly_summary['Client Map - OTE SG (Not capped)'] - combined_quarterly_summary['SW Map - OTE SG (Not capped)']).round(2)


combined_quarterly_summary['Discrepancy 1 - SW Map Expected / Client Map'] = combined_quarterly_summary['Discrepancy 1 - SW Map Expected / Client Map'].astype(float).round(2)

    # Add column for Discrepancy 2 - Client Map - Expected Amount SG

combined_quarterly_summary['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = (combined_quarterly_summary['Payroll - actual SG paid'] - combined_quarterly_summary['Client Map - OTE SG (Not capped)']).round(2)
    
combined_quarterly_summary['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = combined_quarterly_summary['Discrepancy 2 -  Client Map Expected / Payroll Paid'].astype(float).round(2)
# Add column for Discrepancy 3 - SW Map Expected / Payroll paid
combined_quarterly_summary['Discrepancy 3 - SW Map Expected / Payroll paid'] = (combined_quarterly_summary['Payroll - actual SG paid'] - combined_quarterly_summary['SW Map - OTE SG (Not capped)']).round(2)

combined_quarterly_summary['Discrepancy 3 - SW Map Expected / Payroll paid'] = combined_quarterly_summary['Discrepancy 3 - SW Map Expected / Payroll paid'].astype(float).round(2)


combined_quarterly_summary['Discrepancy 1 - SW Comment'] = combined_quarterly_summary.apply(generate_comment, axis=1)


#Inital formula: 
combined_quarterly_summary['Discrepancy 1 - SW Comment'] = combined_quarterly_summary.apply(generate_comment, axis=1)

# Commented out following discussion with Ollie 5/06/2025
# combined_quarterly_summary['OTE (Client + SW Map)'] = np.where(
#     (combined_quarterly_summary['Client Mapping'] == 'Y') & (combined_quarterly_summary['SW mapping'] != 'OTE'),
#     combined_quarterly_summary['Client mapping - OTE'],
#     np.where(
#         (combined_quarterly_summary['Client Mapping'] == 'N') & (combined_quarterly_summary['SW mapping'] == 'OTE'),
#         combined_quarterly_summary['SW Map - OTE (not capped)'],
#         combined_quarterly_summary['SW Map - OTE (not capped)']
#     )
# )

# combined_quarterly_summary['OTE SG (Client + SW Map)'] = np.where(
#     (combined_quarterly_summary['Client Mapping'] == 'Y') & (combined_quarterly_summary['SW mapping'] != 'OTE'),
#     combined_quarterly_summary['Client Mapping - OTE SG Expected'],
#     np.where(
#         (combined_quarterly_summary['Client Mapping'] == 'N') & (combined_quarterly_summary['SW mapping'] == 'OTE'),
#         combined_quarterly_summary['SW Map - OTE SG (Not capped)'],
#         combined_quarterly_summary['SW Map - OTE SG (Not capped)']
#     )
# )


combined_quarterly_summary.to_csv('Payroll_Detail.csv', index=False)
# Problem is that its looking at the current data frame not the instance of the data frame that was used to create the grouped results

# If Payroll - actual SG paid_CumSum == 0 then SW - Final Comment = "SG paid is 0" in paynumber





# Need to create a dataframe that gets the Amount for quarter rather than the individual pay numbers
quarter_sum = combined_quarterly_summary









agg_methods = {\
        'Entity' : 'first',
        'Emp.Code' : 'first',
        'Full_Name': 'first',  
        'Pay_Number': 'last',
        'Unique_Key': 'last',
        #'Line': 'first',
        'Hours/Value': 'sum',
        'Pay_Rate': 'mean',
        'Amount': 'sum',
        'SG_Rate': 'mean',
        'FY_Q': 'first',
        'Financial_Year': 'first', 
        #'Client Mapping': 'first',
        #'SW mapping': 'first',
        'Client Map - OTE (not capped)': 'sum',
        'SW Map - OTE (not capped)': 'sum',
        'SW Map - S&W (not capped)': 'sum',
        'Client Map - OTE SG (Not capped)': 'sum',
        'SW Map - OTE SG (Not capped)': 'sum', 
        'SW Map - S&W SG (Not capped)': 'sum',
        'Payroll - actual SG paid': 'sum', 
        'SCH - actual SG received': 'sum',
        'MCB' : 'first'
        # 'OTE (Client + SW Map)': 'sum',
        # 'OTE SG (Client + SW Map)': 'sum'
        # 'Payroll - actual SG paid_CumSum' : 'last',
        # 'Client Mapping - OTE SG Expected_CumSum' : 'last',
        # 'SW Map - OTE SG expected_CumSum' : 'last',
        #'Discrepancy 1 - SW Comment': 'first'

    }






# Check if required columns exist in DataFrame
#group_by_columns = ['QtrEMPLID', 'Pay_Number']
group_by_columns = ['QtrEMPLID', 'Period_Ending']
missing_cols = [col for col in group_by_columns if col not in quarter_sum.columns]

if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Perform aggregation
quarter_sum = quarter_sum.groupby(group_by_columns).agg(agg_methods).reset_index()


quarter_sum['Pay_Rate'] = quarter_sum['Pay_Rate'].astype(float).round(2)

#quarter_sum['Discrepancy 1 - SW Comment'] =''

# Group by 'Pay_Number' and concatenate 'Discrepancy 1 - SW Comment' values
comment_concat = (
    combined_quarterly_summary
    #.groupby('Pay_Number')['Discrepancy 1 - SW Comment']
    .groupby('Unique_Key')['Discrepancy 1 - SW Comment']
    .apply(lambda x: ' | '.join(x.dropna().astype(str)))
    .reset_index()
)



# Merge the concatenated comment back correctly
#quarter_sum = quarter_sum.merge(comment_concat, on='Pay_Number', how='left')
quarter_sum = quarter_sum.merge(comment_concat, on='Unique_Key', how='left')

# Rename the merged column to match your naming standard (optional)
# quarter_sum = quarter_sum.rename(columns={
#     'Discrepancy 1 - SW Comment': 'Discrepancy_1_SW_Comment_Concat'
# })




def generate_comment1(row):
    if row['Payroll - actual SG paid'] == 0:
        #return f"No Super was paid under pay run number: {row['Pay_Number']}"
        return f"No Super was paid under pay run unique key: {row['Unique_Key']}"
    elif row['Client Map - OTE SG (Not capped)'] == 0:
        #return f"Client Mapping didn't make payment under pay run number: {row['Pay_Number']}"
        return f"Client Mapping didn't make payment under pay run unique key: {row['Unique_Key']}"
    # Adde 4/06/2025 as per OM advise
    elif row['Client Map - OTE SG (Not capped)'] != row['Payroll - actual SG paid']:
        #return f"Underpayment within pay run number: {row['Pay_Number']}" if row['Client Map - OTE SG (Not capped)'] > row['Payroll - actual SG paid'] else f"Overpayment under pay run number: {row['Pay_Number']}"
        return f"Underpayment within pay unique key: {row['Unique_Key']}" if row['Client Map - OTE SG (Not capped)'] > row['Payroll - actual SG paid'] else f"Overpayment under pay unique key: {row['Unique_Key']}"
    else:
        return row.get('Discrepancy 2 - SW Comment', '')



def generate_comment2(row):
    
    if row['Payroll - actual SG paid'] == 0:
        #return f"No Super was paid under pay run number: {row['Pay_Number']}"
        return f"No Super was paid under pay unique key: {row['Unique_Key']}"
    elif row['SW Map - OTE SG (Not capped)'] == 0:
        #return f"SW Mapping didn't make payment under pay run number: {row['Pay_Number']}"
        return f"SW Mapping didn't make payment under pay unique key: {row['Unique_Key']}"
        
    
    else:
        return row.get('Discrepancy 3 - SW Comment', '')



quarter_sum['Discrepancy 2 - SW Comment'] = quarter_sum.apply(generate_comment1, axis=1)
quarter_sum['Discrepancy 3 - SW Comment'] = quarter_sum.apply(generate_comment2, axis=1)



quarter_sum.to_csv('Quarterly_Sum.csv', index=False)






def SG_actual_Vs_SW_Map(df, output_dir="output"):
    # Define aggregation methods
    agg_methods = {\
        'Entity' : 'first',
        'Emp.Code' : 'first',
        'Full_Name': 'first',  
        'Pay_Number': 'first',
        'Unique_Key': 'first',
        #'Line': 'first',
        'Hours/Value': 'sum',
        'Pay_Rate': 'mean',
        'Amount': 'sum',
        'SG_Rate': 'mean',
        'FY_Q': 'first',
        'Financial_Year': 'first', 
        #'Client Mapping': 'first',
        #'SW mapping': 'first',
        'Client Map - OTE (not capped)': 'sum',
        'SW Map - OTE (not capped)': 'sum',
        'SW Map - S&W (not capped)': 'sum',
        'Client Map - OTE SG (Not capped)': 'sum',
        'SW Map - OTE SG (Not capped)': 'sum', 
        'SW Map - S&W SG (Not capped)': 'sum',
        'Payroll - actual SG paid': 'sum', 
        'SCH - actual SG received': 'sum',
        'MCB' : 'first'
        # 'OTE (Client + SW Map)': 'sum',
        # 'OTE SG (Client + SW Map)': 'sum'
        
        # 'Payroll - actual SG paid_CumSum' : 'last',
        # 'Client Mapping - OTE SG Expected_CumSum' : 'last',
        # 'SW Map - OTE SG expected_CumSum' : 'last'

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
    
    # def generate_comment_Discrep_3 (row):
    #     if row['Discrepancy 1 - SW Map Expected / Client Map'] == row['Discrepancy 3 - SW Map Expected / Payroll paid']:
    #         return f"Mapping issue with pay run: {row['Pay_Number']} "
    #         #Pay Description: {row['Pay Description']}"
        
    #     elif row['Discrepancy 2 -  Client Map Expected / Payroll Paid'] == row['Discrepancy 3 - SW Map Expected / Payroll paid']:
    #        # return f"Payroll issue with pay run: {row['Pay_Number']} "
    #         return f"Refer to Discrepancy 2 - Client Map Expected / Payroll Paid for more details. Pay run: {row['Pay_Number']} "
    #     # Pay Description: {row['Pay Description']}"

    #     elif row['Discrepancy 3 - SW Map Expected / Payroll paid'] == row['Discrepancy 1 - SW Map Expected / Client Map'] + row['Discrepancy 2 -  Client Map Expected / Payroll Paid']:
    #         return f"Mapping and Payroll issue with pay run: {row['Pay_Number']} refer to Discrepancy 1 and 2 for more details"
        
    #     elif row['Discrepancy 1 - SW Map Expected / Client Map'] or row['Discrepancy 2 -  Client Map Expected / Payroll Paid'] != row['Discrepancy 3 - SW Map Expected / Payroll paid']:
    #         return f"unknown issue with pay run: {row['Pay_Number']} "
    #         # Pay Description: {row['Pay Description']}"


      

    def generate_comment_Discrep_3(row):
        disc1 = row['Discrepancy 1 - SW Map Expected / Client Map']
        disc2 = row['Discrepancy 2 -  Client Map Expected / Payroll Paid']
        disc3 = row['Discrepancy 3 - SW Map Expected / Payroll paid']

        if np.isclose(disc1, disc3, atol=0.07):
           # return f"Mapping issue with pay run: {row['Pay_Number']}"
            return f"Mapping issue with pay run: {row['Unique_Key']} "

        elif np.isclose(disc2, disc3, atol=0.07):
            #return f"Refer to Discrepancy 2 - Client Map Expected / Payroll Paid for more details. Pay run: {row['Pay_Number']}"
            return f"Refer to Discrepancy 2 - Client Map Expected / Payroll Paid for more details. Pay run: {row['Unique_Key']} "

        elif np.isclose(disc3, disc1 + disc2, atol=0.03):
            #return f"Mapping and Payroll issue with pay run: {row['Pay_Number']} refer to Discrepancy 1 and 2 for more details"
            return f"Mapping and Payroll issue with pay run: {row['Unique_Key']} refer to Discrepancy 1 and 2 for more details"

        else:
            #return f"Unknown issue with pay run: {row['Pay_Number']}"
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
       #'SCH - actual SG received', 
       'MCB',
       #'SG up to MCB client map',
       #'SG up to MCB SW map',
       'Payroll - actual SG paid', 
       #'SG Paid => SG up to cap',

        # 'OTE (Client + SW Map)', 'OTE SG (Client + SW Map)',
        # 'Payroll - actual SG paid_CumSum',
        # 'Client Mapping - OTE SG Expected_CumSum',
        # 'SW Map - OTE SG expected_CumSum',
        'Discrepancy 1 - SW Map Expected / Client Map',
       'Discrepancy 2 -  Client Map Expected / Payroll Paid',
       'Discrepancy 3 - SW Map Expected / Payroll paid',
       'Discrepancy 1 - SW Comment', 'Discrepancy 2 - SW Comment',
       'Discrepancy 3 - SW Comment']

        
    # Reorder the DataFrame columns
    grouped_df = grouped_df[column_order]




    # grouped_df['Diff_MCB_Vs_OTE_(Client + SW Map)'] = grouped_df['MCB'] - grouped_df['OTE (Client + SW Map)']
    # grouped_df['Diff_MCB_Vs_OTE_(Client + SW Map)'] = grouped_df['Diff_MCB_Vs_OTE_(Client + SW Map)'].astype(float).round(2)


    # grouped_df['Above / Below Cap (Client + SW Map)'] = np.where(
    #   grouped_df['Diff_MCB_Vs_OTE_(Client + SW Map)'] < 0, 'Above Cap',
    #     np.where(grouped_df['Diff_MCB_Vs_OTE_(Client + SW Map)'] > 0, 'Below Cap', 'Cap Met')
    # )
    # grouped_df['Above / Below Cap (Client + SW Map)'] = grouped_df['Above / Below Cap (Client + SW Map)'].astype(str)

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

    # grouped_df['SW Map - OTE SG (Capped to MCB)'] = np.where(
    #     grouped_df['SW Map - OTE (not capped)'] == (grouped_df['MCB']), grouped_df['MCB'] * grouped_df['SG_Rate'],
    #     np.where(
    #         grouped_df['SW Map - OTE (not capped)'] > (grouped_df['MCB']),
    #         grouped_df['MCB'] * grouped_df['SG_Rate']
    #     ),
    #     grouped_df['SW Map - OTE (not capped)'] * grouped_df['SG_Rate']
    # )

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
    #grouped_df.loc[mask, 'Discrepancy 2 - SW Comment'] = "No Discrepancy / Immaterial"

    
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


    # # Assuming your DataFrame is df and the column is 'Discrepancy 1 - SW Comment'
    # valid_comment_mask = grouped_df['Discrepancy 1 - SW Comment'].str.contains(
    #     r'No payment under Client Mapping|SW Mapping didn\'t classify line|Pay Description:', 
    #     na=False
    # )

    # # Apply the filter
    # grouped_df = grouped_df[valid_comment_mask].copy()
    

    #grouped_df['Discrepancy 1 - SW Comment'] = df['Discrepancy 1 - SW Comment'].apply(lambda x: re.sub(r'\s*\|\s*(?=\s*\|)', '', str(x)).strip('| '))


    # Maybe should three columns for Materality and one for the comment

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
       #'SCH - actual SG received', 
       'MCB',
       'Client Map - OTE SG (Capped to MCB)',
       'SW Map - OTE SG (Capped to MCB)',
       #'SG up to MCB client map',
       #'SG up to MCB SW map',
       'Payroll - actual SG paid', 
       'SG Paid => SG up to cap',

        # 'OTE (Client + SW Map)', 'OTE SG (Client + SW Map)',
        # 'Payroll - actual SG paid_CumSum',
        # 'Client Mapping - OTE SG Expected_CumSum',
        # 'SW Map - OTE SG expected_CumSum',
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



unique_comments = combined_result_df.copy()

# Create the combined 'FY&Q' column
unique_comments["FY&Q"] = unique_comments["Financial_Year"].astype(str) + "_" + unique_comments["FY_Q"].astype(str)

# Select only the required columns
unique_comments = unique_comments[['FY&Q', 'Discrepancy 1 - SW Comment', 'Discrepancy 2 - SW Comment', 'Discrepancy 3 - SW Comment']]

# Drop duplicate rows
unique_comments = unique_comments.drop_duplicates()



unique_comments['Comment 1 - Count'] = unique_comments['Discrepancy 1 - SW Comment'].apply(lambda x: x.count('|') + 1 if isinstance(x, str) else 0)
unique_comments['Comment 2 - Count'] = unique_comments['Discrepancy 2 - SW Comment'].apply(lambda x: x.count('|') + 1 if isinstance(x, str) else 0)
unique_comments['Comment 3 - Count'] = unique_comments['Discrepancy 3 - SW Comment'].apply(lambda x: x.count('|') + 1 if isinstance(x, str) else 0)
unique_comments['Total Comments'] = unique_comments['Comment 1 - Count'] + unique_comments['Comment 2 - Count'] + unique_comments['Comment 3 - Count']

unique_comments = unique_comments.sort_values(by='FY&Q')

unique_comments['No Payment Under Client Mapping - Comment Count'] = unique_comments.apply(
    lambda row: sum(1 for comment in [row['Discrepancy 1 - SW Comment'], row['Discrepancy 2 - SW Comment'], row['Discrepancy 3 - SW Comment']] if 'No payment under Client Mapping' in str(comment)),
    axis=1
)

unique_comments['SW Mapping Didn\'t Classify Line - Comment Count'] = unique_comments.apply(
    lambda row: sum(1 for comment in [row['Discrepancy 1 - SW Comment'], row['Discrepancy 2 - SW Comment'], row['Discrepancy 3 - SW Comment']] if 'Overpayment, SW Mapping' in str(comment)),
    axis=1
)

# Your unique descriptions list
unique_descriptions = [
    'Additional Hours: LEAVE LOADING 17.5%',
    'Vehicle Allowance as OTE',
    'MV ALLOWANCE GC as OTE',
    'Leave Loading',
    'LEAVE LOADING 17.5%',
    'Ordinary',
    'ANNUAL LEAVE LOADING',
    'Staff Training Day'
]

# Function to check if a comment is an Overpayment or Under payment
def is_over_under_payment(comment):
    comment = str(comment)
    return 'Overpayment' in comment or 'No payment' in comment

def is_under_payment(comment):
    comment = str(comment)
    return 'Underpayment' in comment or 'No payment' in comment

def is_Over_payment(comment):
    comment = str(comment)
    return 'Overpayment' in comment 

def is_No_Super(comment):
    comment = str(comment)
    return 'No Super' in comment

def client_mapping(comment):
    comment = str(comment)
    return 'Client Mapping' in comment

def SW_mapping(comment):
    comment = str(comment)
    return 'SW Mapping' in comment

def refer_to_discrepancy_1(comment):
    comment = str(comment)
    return 'Refer to Discrepancy 1' in comment 


def refer_to_discrepancy_2(comment):
    comment = str(comment)
    return 'Refer to Discrepancy 2' in comment

def Mapping_and_Payroll(comment):
    comment = str(comment)
    return 'Mapping and Payroll issue' in comment

def Mapping_issue(comment):
    comment = str(comment)
    return 'Mapping issue with pay run' in comment

# Create a new column for each unique description to count matches
for desc in unique_descriptions:
    unique_comments[f'{desc} - Under Payment Count - Discrep 1'] = unique_comments.apply(
        lambda row: sum(
            1 for comment in [row['Discrepancy 1 - SW Comment']]
            if str(comment).strip().endswith(desc) and is_under_payment(comment)
        ),
        axis=1
    )

for desc in unique_descriptions:
    unique_comments[f'{desc} - Over Payment Count - Discrep 1'] = unique_comments.apply(
        lambda row: sum(
            1 for comment in [row['Discrepancy 1 - SW Comment']]
            if str(comment).strip().endswith(desc) and is_Over_payment(comment)
        ),
        axis=1
    )

unique_descriptions_2 = [
    'Underpayment within pay run number'
]


unique_descriptions_3 = [
    'Overpayment within pay run number']

unique_descriptions_3_1 = [
    'Overpayment'
]

unique_descriptions_4 = [
    'No Super was paid under pay run number'
]

unique_descriptions_5 = [
    'Client Mapping'
]

unique_descriptions_6 = [
    'Mapping and Payroll issue'
]

unique_descriptions_7 = [
    'Refer to Discrepancy 2'
]

unique_descriptions_8 = [
    'Mapping issue with pay run'
]

unique_descriptions_9 = [
    'SW Mapping'
]

unique_descriptions_10 = [
    'Refer to Discrepancy 2'
]


unique_descriptions_11 = [
    'Refer to Discrepancy 1'
]

for desc in unique_descriptions_2:
    unique_comments['Under Payment Count - Discrep 2'] = unique_comments.apply(
        lambda row: str(row['Discrepancy 2 - SW Comment']).count(desc) if is_under_payment(row['Discrepancy 2 - SW Comment']) else 0,
        axis=1
    )
 
for desc in unique_descriptions_3:
    unique_comments['Over Payment Count - Discrep 2'] = unique_comments.apply(
        lambda row: str(row['Discrepancy 2 - SW Comment']).count(desc) if is_Over_payment(row['Discrepancy 2 - SW Comment']) else 0,
        axis=1
    )


# for desc in unique_descriptions_4:
#     unique_comments['No Super Count - Discrep 2'] = unique_comments.apply(
#         lambda row: sum(
#             1 for comment in [row['Discrepancy 2 - SW Comment']]
#             if str(comment).strip().__contains__(desc) and is_No_Super(comment)
#         ),
#         axis=1
#     )
for desc in unique_descriptions_4:
    unique_comments['No Super Count - Discrep 2'] = unique_comments.apply(
        lambda row: str(row['Discrepancy 2 - SW Comment']).count(desc) if is_No_Super(row['Discrepancy 2 - SW Comment']) else 0,
        axis=1
    )


for desc in unique_descriptions_5:
    unique_comments['Client Mapping No Pay Count - Discrep 2'] = unique_comments.apply(
        lambda row: str(row['Discrepancy 2 - SW Comment']).count(desc) if client_mapping(row['Discrepancy 2 - SW Comment']) else 0,
        axis=1
    )



for desc in unique_descriptions_11:
    unique_comments['Refer to Discrepancy 1 Count - Discrep 3'] = unique_comments.apply(
        lambda row: sum(
            1 for comment in [row['Discrepancy 3 - SW Comment']]
            if str(comment).strip().endswith(desc) and refer_to_discrepancy_1(comment)
        ),
        axis=1
    )

for desc in unique_descriptions_6:
    unique_comments['Mapping and Payroll issue Count - Discrep 3'] = unique_comments.apply(
        lambda row: str(row['Discrepancy 3 - SW Comment']).count(desc) if Mapping_and_Payroll(row['Discrepancy 3 - SW Comment']) else 0,
        axis=1
    )


for desc in unique_descriptions_7:
    unique_comments['Refer to Discrepancy 2 Count - Discrep 3'] = unique_comments.apply(
        lambda row: str(row['Discrepancy 3 - SW Comment']).count(desc) if refer_to_discrepancy_2(row['Discrepancy 3 - SW Comment']) else 0,
        axis=1
    )


unique_comments['Comment 3 - in Depth'] = np.where(
    unique_comments['Discrepancy 3 - SW Comment'].str.contains('Refer to Discrepancy 1', na=False),
    unique_comments['Discrepancy 1 - SW Comment'],
    np.where(
        unique_comments['Discrepancy 3 - SW Comment'].str.contains('Refer to Discrepancy 2', na=False),
        unique_comments['Discrepancy 2 - SW Comment'],
    np.where(
        unique_comments['Discrepancy 3 - SW Comment'].str.contains('Mapping and Payroll issue', na=False),
        unique_comments['Discrepancy 3 - SW Comment'],
        'N/a'
    )
    )
)


for desc in unique_descriptions_2:
    unique_comments['Under Payment Count - Discrep 3 in Depth'] = unique_comments.apply(
        lambda row: sum(
            1 for comment in [row['Comment 3 - in Depth']]
            if str(comment).strip().count(desc) and is_under_payment(comment)
        ),
        axis=1
    )



for desc in unique_descriptions_3_1:
    unique_comments['Over Payment Count - Discrep 3 in Depth'] = unique_comments.apply(
        lambda row: str(row['Comment 3 - in Depth']).count(desc) if is_Over_payment(row['Comment 3 - in Depth']) else 0,
        axis=1
    )


for desc in unique_descriptions_4:
    unique_comments['No Super Count - Discrep 3 in Depth'] = unique_comments.apply(
        lambda row: sum(
            1 for comment in [row['Comment 3 - in Depth']]
            if str(comment).strip().count(desc) and is_No_Super(comment)
        ),
        axis=1
    )

# for desc in unique_descriptions_5:
#     unique_comments['Client Mapping No Pay Count - Discrep 3 in Depth'] = unique_comments.apply(
#         lambda row: sum(
#             1 for comment in [row['Comment 3 - in Depth']]
#             if str(comment).strip().count(desc) and client_mapping(comment)
#         ),
#         axis=1
#     )

for desc in unique_descriptions_5:
    unique_comments['Client Mapping No Pay Count - Discrep 3 in Depth'] = unique_comments.apply(
        lambda row: str(row['Comment 3 - in Depth']).count(desc) if client_mapping(row['Comment 3 - in Depth']) else 0,
        axis=1
    )


# commented out due to no need for this column - 1/07/2025
# for desc in unique_descriptions_8:
#     unique_comments['Mapping issue Count - Discrep 3'] = unique_comments.apply(
#         lambda row: str(row['Discrepancy 3 - SW Comment']).count(desc) if Mapping_issue(row['Discrepancy 3 - SW Comment']) else 0,
#         axis=1
#     )

# for desc in unique_descriptions_4:
#     unique_comments[f'{desc} - No Super Count - Discrep 3'] = unique_comments.apply(
#         lambda row: str(row['Discrepancy 3 - SW Comment']).count(desc) if is_No_Super(row['Discrepancy 3 - SW Comment']) else 0,
#         axis=1
#     )

    
# Export to CSV
unique_comments.to_csv('unique_comments.csv', index=False)

#def commentary(combined_result_df, output_dir="output"):
"""
    Generates commentary based on discrepancies in the DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing payroll data.
    output_dir (str): Directory where the output CSV should be saved.

    Returns:
    pd.DataFrame: DataFrame with added commentary columns.
    """
# Step 1: Create a filtered DataFrame


Discprepancy_1 = combined_result_df[combined_result_df['Discrepancy 1 - SW Map Expected / Client Map'] != 0]
Discprepancy_2 = combined_result_df[combined_result_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'] != 0]
Discprepancy_3 = combined_result_df[combined_result_df['Discrepancy 3 - SW Map Expected / Payroll paid'] != 0]

# get unique QtrEMPLID for Discrepancy 1
Discp1_unique_QtrEMPLID = Discprepancy_1['QtrEMPLID'].unique()   

pd.DataFrame(Discp1_unique_QtrEMPLID, columns=['QtrEMPLID']).to_csv('Discp1_unique_QtrEMPLID.csv', index=False)


# Where QtrEMPLID is in the list of unique QtrEMPLID for Discrepancy 1 find rows where combined_quarterly_summary['Client Map - OTE SG (Not capped)'] - combined_quarterly_summary['SW Map - OTE SG (Not capped)'] != 0
# and return the values in columns PayCode and Pay_Number



combined_quarterly_summary_Discp1 = combined_quarterly_summary[combined_quarterly_summary['QtrEMPLID'].isin(Discp1_unique_QtrEMPLID)]



