import sys
print(sys.executable)

import re

import os
from dataframes import(
    process_income_paycodes,
    process_deduction_paycodes,
    process_contribution_paycodes,
    process_allowance_paycodes,
    process_payroll_data,
    process_super_data,
    process_combo_paycodes
)
import pandas as pd
import numpy as np
from pandas import ExcelWriter

# File paths
#Declare File path for Labour Payroll
Payroll_Labour_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Payroll"

#Declare File path for Offshore Payroll
Payroll_Offshore_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Payroll"


#Declare File path for Allowance Paycodes 
allowancePaycodes_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\Allowances_crossEntity.csv"
#Declare File path for Contribution Paycodes 
contributionPaycodes_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\Contributions_crossEntity.csv"
#Declare File path for Deductions Paycodes 
deductionsPaycodes_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\Deductions_crossEntity.csv"
#Declare File path for Income Paycodes 
incomePaycodes_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\Income_crossEntity.csv"
#Declare File path for Employee Labels Labour
Employee_labelsLabour_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Employee details\Employee_Labels.csv"
#Declare File path for Employee Labels Offshore
Employee_labelsOffshore_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Employee details\Employee_Labels.csv"
# Declare File path for Super Labour
Super_Labour_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO LABOUR\Super\CSVs"
# Declare file path for super offshore
Super_Offshore_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\MARITIMO OFFSHORE\Super\CSVs"
# Declare file path for combo paycodes
Combo_Paycodes_filepath = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\Shared Folder\Payroll reports\Paycode_CrossEntity.csv"



# Generate DataFrames
Payroll_Labour_data = process_payroll_data(Payroll_Labour_filepath)
Payroll_Offshore_data = process_payroll_data(Payroll_Offshore_filepath)
#allowancePaycodes = process_allowance_paycodes(allowancePaycodes_filepath)
#contributionPaycodes = process_contribution_paycodes(contributionPaycodes_filepath)
#deductionsPaycodes = process_deduction_paycodes(deductionsPaycodes_filepath)
#incomePaycodes = process_income_paycodes(incomePaycodes_filepath)
Super_Labour_data = process_super_data(Super_Labour_filepath)
Super_Offshore = process_super_data(Super_Offshore_filepath)
combo_Paycodes = process_combo_paycodes(Combo_Paycodes_filepath)



#12/02/2025 Next step is to look at how we merge the paycode dataframes into the Payroll data or at least make reference to it



def payroll_calc(Payroll_Offshore_data, combo_Paycodes, file_suffix="LABOUR / OFFSHORE"):
    global merged_data
    merged_data = Payroll_Offshore_data.merge(
        combo_Paycodes,
        how="left",
        left_on="PayCode",
        right_on="PayCode"
    )
    
   #print(merged_data.head())  # Check first few rows after merge
   #print(merged_data.isnull().sum())  # Check for null values

    # Remove duplicates
    rows_before = len(merged_data)
    merged_data = merged_data.drop_duplicates()
    rows_after = len(merged_data)
    print(f"Number of duplicates dropped: {rows_before - rows_after}")



    merged_data['Period_Ending'] = pd.to_datetime(merged_data['Period_Ending'])
    

   

    merged_data['FY_Q'] = np.where(
        merged_data['Period_Ending'].dt.month.isin([7, 8, 9]), 'Q1',
        np.where(
            merged_data['Period_Ending'].dt.month.isin([10, 11, 12]), 'Q2',
            np.where(
                merged_data['Period_Ending'].dt.month.isin([1, 2, 3]), 'Q3',
                np.where(
                    merged_data['Period_Ending'].dt.month.isin([4, 5, 6]), 'Q4',
                    'Unknown'  # Use a string instead of np.nan to avoid dtype mismatch
                )
            )
        )
    )

        # Assign the financial year (FY) based on the ending period
    merged_data['Financial_Year'] = np.where(
        merged_data['Period_Ending'].dt.month >= 7,
        merged_data['Period_Ending'].dt.year + 1,  # July–Dec belongs to the next FY
        merged_data['Period_Ending'].dt.year  # Jan–June belongs to the current FY
    )

    # Fill NaN values before converting to int
    merged_data['Financial_Year'] = merged_data['Financial_Year'].fillna(0).astype(int)


    # Combine FY and Quarter
    merged_data['FY_Q_Label'] = 'FY' + merged_data['Financial_Year'].astype(str) + '_' + merged_data['FY_Q']



    
    # Assign SG Rate based on Period_Ending year
    merged_data['SG_Rate'] = np.where(
        merged_data['Financial_Year'] == 2021, 0.095,
        np.where(
            merged_data['Financial_Year'] == 2022, 0.1,
            np.where(
                merged_data['Financial_Year'] == 2023, 0.105,
                np.where(
                    merged_data['Financial_Year'] == 2024, 0.11,
                    np.where(
                        merged_data['Financial_Year'] == 2025, 0.115,
                        np.where(
                            merged_data['Financial_Year'] == 2026, 0.12,
                            np.nan  # Use np.nan for years not specified
                        )
                    )
                )
            )
        )
    )
    
    
    
    # Read Paycode Mapping

    PayMap = r"C:\Users\smits\OneDrive - SW Accountants & Advisors Pty Ltd\Desktop\Maritimo\2025.05.21_PAYCODE_MAPPING.xlsx"

    paycode_mapping = pd.read_excel(PayMap, sheet_name='UPDATED MAPPING')

    

    paycode_mapping['Combined_PayCode'] = paycode_mapping['PayCode'].astype(str) + '_' + paycode_mapping['Description'].astype(str)

    OTE_paycodesBigBoats = paycode_mapping.loc[
    paycode_mapping['CLIENT MAP FOR SG'] == 'Y', 'Combined_PayCode'
    ].dropna().tolist()

    

    print("Big Boats Paycodes")
    print(OTE_paycodesBigBoats)
    print("Length of Big Boats Paycodes")
    print(len(OTE_paycodesBigBoats))


    

    OTE_paycodesSW = paycode_mapping.loc[
    paycode_mapping['SW MAP'] == 'OTE', 'Combined_PayCode'
    ].dropna().tolist()

    print("SW Paycodes")
    print(OTE_paycodesSW)
    print("Length of SW Paycodes")  
    print(len(OTE_paycodesSW))

    SUPER_paycodesSW = paycode_mapping.loc[
        # Amendment 27/05/25
        #paycode_mapping['SW MAP'] == 'SUPER', 'Combined_PayCode'
        paycode_mapping['SW MAP'] == 'SUPER - SG', 'Combined_PayCode'
    ].dropna().tolist()

    print("Super Paycodes")
    print(SUPER_paycodesSW)
    print("Length of Super Paycodes")
    print(len(SUPER_paycodesSW))


    SnW_paycodesSW = paycode_mapping.loc[
        paycode_mapping['SW MAP'] == 'S&W', 'Combined_PayCode'
    ].dropna().tolist()


    print("S&W Paycodes")
    print(SnW_paycodesSW)
    print("Length of S&W Paycodes")
    print(len(SnW_paycodesSW))

    Tax_paycodesSW = paycode_mapping.loc[
        paycode_mapping['SW MAP'] == 'TAX', 'Combined_PayCode'
    ].dropna().tolist()

    print("Tax Paycodes")
    print(Tax_paycodesSW)
    print("Length of Tax Paycodes")
    print(len(Tax_paycodesSW))

  


    # Get all unique values from both lists
    unique_paycodes = list(set(OTE_paycodesBigBoats + OTE_paycodesSW))

    # Print the result
    print('unique_paycodes')
    print(unique_paycodes)

    merged_data['Combined_PayCode'] = merged_data['PayCode'].astype(str) + '_' + merged_data['Description_x'].astype(str)

    merged_data['Client Mapping'] = np.where(
         merged_data['Combined_PayCode'].isin(OTE_paycodesBigBoats),
        'Y',
        'N'
    )

    merged_data['SW mapping'] = np.where(
        merged_data['Combined_PayCode'].isin(OTE_paycodesSW),
        'OTE',
        np.where(
            merged_data['Combined_PayCode'].isin(SnW_paycodesSW),
            'S&W',
            np.where(
                merged_data['Combined_PayCode'].isin(SUPER_paycodesSW),
                'SUPER',
                np.where(
                    merged_data['Combined_PayCode'].isin(Tax_paycodesSW),
                    'TAX',
                    'N/A'  # Use a string instead of np.nan to avoid dtype mismatch

                )
            )
        )
    )
    

    
    # Calculate OTE amounts for Client and SW OTE mappings
    merged_data['Client mapping - OTE'] = np.where(
        merged_data['Combined_PayCode'].isin(OTE_paycodesBigBoats),
        merged_data['Total'],
        0
    )
    
    merged_data['SW Mapping - OTE'] = np.where(
        merged_data['Combined_PayCode'].isin(OTE_paycodesSW),
        merged_data['Total'],
        0
    )

    merged_data['SW Mapping - S&W'] = np.where(
        merged_data['Combined_PayCode'].isin(SnW_paycodesSW),
        merged_data['Total'],
        0
    )

    # Test 28/04/25
    # merged_data['Client Mapping - S&W'] = np.where(
    #     merged_data['PayCode'].isin(OTE_paycodesBigBoats),
    #     0,
    #     merged_data['Total']
    # )

    
    # Calculate SG Actuals and Expected
    merged_data['Client Mapping - OTE SG Expected'] = np.where(
        merged_data['Combined_PayCode'].isin(OTE_paycodesBigBoats),
        merged_data['Total'] * merged_data['SG_Rate'],
        0
    )

    merged_data['Client Mapping - OTE SG Expected'] = merged_data['Client Mapping - OTE SG Expected'].astype(float).round(2)

    
    
    merged_data['SW Map - OTE SG expected'] = np.where(
        merged_data['Combined_PayCode'].isin(OTE_paycodesSW),
        merged_data['Total'] * merged_data['SG_Rate'],
        0
    )

    merged_data['SW Map - OTE SG expected'] = merged_data['SW Map - OTE SG expected'].astype(float).round(2)


    merged_data['SW Map - S&W SG'] = merged_data['SW Mapping - S&W'] * merged_data['SG_Rate']

   

    

    merged_data['Payroll - actual SG paid'] = np.where(
        merged_data['Combined_PayCode'].isin(SUPER_paycodesSW),
        merged_data['Total'], 
        0
    )

    merged_data['SCH - actual SG received'] = 0 

    

    #merged_data['S&W - Client to SW Map Discrepancy'] = merged_data['Client Mapping - S&W'] - merged_data['SW Mapping - S&W']

    merged_data['OTE SG Expected - Client to SW Map Discrepancy'] = merged_data['Client Mapping - OTE SG Expected'] - merged_data['SW Map - OTE SG expected']

    #merged_data['S&W SG Expected - Client to SW Map Discrepancy'] = merged_data['Client Map - S&W SG'] - merged_data['SW Map - S&W SG']

    # # Compute the difference
    # merged_data['Super_Diff'] = (
    #     merged_data['SW Map - OTE SG expected'] - merged_data['Client Mapping - OTE SG Expected']
    # )

    merged_data['QtrEMPLID'] = merged_data['Emp.Code'].astype(str) + '_' + merged_data['FY_Q_Label']
    
    # Define the desired column order
    column_order = [
        'QtrEMPLID', 'Period_Ending', 'FY_Q', 'Financial_Year', 'FY_Q_Label',  # New columns placed after 'Period_Ending'
        'Emp.Code', 'Full_Name', 'Pay_Number', 'Line', 'Combined_PayCode', 'PayCode', 'Description_x', 'Hours/Value', 
        'Pay_Rate', 'Total', 'Cost_Centre', 'Emp_Group', 'PayCode_Type', 'Description_y', 'Type',
        'Tax_Status_Income_Category', 'Formula', 'Value', 'Fixed_Variable', 'Tax_Cert_Status', 'Min_$', 
        'Max_$', 'Min_Qty', 'Max_Qty', 'Super_on_Pay_Advice', 'Show_rate_on_Pay_Advice',
        'Show_YTD_on_Pay_Advice', 'Allow_Data_Entry', 'Multiple_G_L_Dissections', 'Show_on_Pay_Advice',
        'Include_in_SG_Threshold', 'Frequency', 'Super_for_Casuals_Under_18', 'Reduce_Hours', 'Inactive',
        'Calculation_Table', 'WCOMP', 'Days_Date', 'Back_Pay', 'Count_from', 'Disperse_over_Cost_Centres',
        'Quarterly_Value_Maximum', 'Monthly_Threshold', 'SG_Rate', 
        'Client Mapping', 'SW mapping', 'Client mapping - OTE', 'SW Mapping - OTE', 'SW Mapping - S&W',
        'Client Mapping - OTE SG Expected',
        'SW Map - OTE SG expected' , 'SW Map - S&W SG', 'Payroll - actual SG paid', 'SCH - actual SG received'
        # , 'Super_Diff'
    ]

        
    # Reorder the DataFrame columns
    merged_data = merged_data[column_order]

    columns_to_drop = ['Cost_Centre', 'Emp_Group', 'PayCode_Type', 'Description_y', 'Type',
        'Tax_Status_Income_Category', 'Formula', 'Value', 'Fixed_Variable', 'Tax_Cert_Status', 'Min_$', 
        'Max_$', 'Min_Qty', 'Max_Qty', 'Super_on_Pay_Advice', 'Show_rate_on_Pay_Advice',
        'Show_YTD_on_Pay_Advice', 'Allow_Data_Entry', 'Multiple_G_L_Dissections', 'Show_on_Pay_Advice',
        'Include_in_SG_Threshold', 'Frequency', 'Super_for_Casuals_Under_18', 'Reduce_Hours', 'Inactive',
        'Calculation_Table', 'WCOMP', 'Days_Date', 'Back_Pay', 'Count_from', 'Disperse_over_Cost_Centres',
        'Quarterly_Value_Maximum', 'Monthly_Threshold']

     # Drop unneeded columns if provided
   
    merged_data = merged_data.drop(columns=columns_to_drop, errors='ignore')  # ignore errors if columns don't exist

    merged_data = merged_data.rename(columns={'Description_x': 'Description'})


    
    # Save to CSV with dynamic suffix
    filename = f"payroll_data_{file_suffix}.csv"
    merged_data.to_csv(filename, index=False)
    print(f"Saved to {filename}")

    
    return merged_data





payroll_calc(Payroll_Labour_data, combo_Paycodes, file_suffix="LABOUR")
payroll_calc(Payroll_Offshore_data, combo_Paycodes, file_suffix="OFFSHORE")

mergedData_Labour = payroll_calc(Payroll_Labour_data, combo_Paycodes, file_suffix="LABOUR")
mergedData_Offshore = payroll_calc(Payroll_Offshore_data, combo_Paycodes, file_suffix="OFFSHORE")


print(mergedData_Labour.columns)



def calculate_shortfall_offset(mergedData_Labour):
    agg_methods = {
        'Full_Name': 'first',  
        'Line': 'first',
        'Description': 'first',
        'Hours/Value': 'sum',
        'Pay_Rate': 'mean',
        'Total': 'sum',
        'SG_Rate': 'mean',
        'FY_Q': 'first',
        'Financial_Year': 'first', 
        'Client Mapping': 'first',
        'SW mapping': 'first',
        'Client mapping - OTE': 'sum',
        'SW Mapping - OTE': 'sum',
        'SW Mapping - S&W': 'sum',
        'Client Mapping - OTE SG Expected': 'sum',
        'SW Map - OTE SG expected': 'sum', 
        'SW Map - S&W SG': 'sum',
        'Payroll - actual SG paid': 'sum', 
        'SCH - actual SG received': 'sum'
    }


    df1 = mergedData_Labour.groupby(['Period_Ending', 'Pay_Number', 'Emp.Code']).agg(agg_methods).reset_index()
    df1 = df1.sort_values(by=['Emp.Code', 'Period_Ending'])

    df1['Pay_Rate'] = df1['Pay_Rate'].astype(float).round(2)

    df1['SW Map - OTE SG expected'] = df1['SW Map - OTE SG expected'].round(2)
    df1['Shortfall SG'] = df1['Payroll - actual SG paid'] - df1['SW Map - OTE SG expected']
    df1['clumative_sum'] = df1.groupby(['Emp.Code'])['Shortfall SG'].cumsum()

    df1 = df1.sort_values(by=['Emp.Code', 'Period_Ending'])

    df1['cumulative_sum_12Months_OVERPAY'] = df1.groupby('Emp.Code').apply(
        lambda g: g.apply(
            lambda row: g.loc[
                (g['Period_Ending'] > row['Period_Ending'] - pd.DateOffset(years=1)) &
                (g['Period_Ending'] <= row['Period_Ending']) &
                (g['Shortfall SG'] > 0.01),
                'Shortfall SG'
            ].sum(), axis=1)
    ).reset_index(level=0, drop=True)

    df1['Adjust_shortfall_Y/N'] = np.where(
        (df1['Shortfall SG'] < 0) & (df1['cumulative_sum_12Months_OVERPAY'] > 0), 'Y', 'N'
    )

    df1['cumulative_sum_12Months'] = df1.groupby('Emp.Code').apply(
        lambda g: g.apply(
            lambda row: g.loc[
                (g['Period_Ending'] > row['Period_Ending'] - pd.DateOffset(years=1)) &
                (g['Period_Ending'] <= row['Period_Ending']) &
                (g['Adjust_shortfall_Y/N'] == 'Y'),
                'Shortfall SG'
            ].sum(), axis=1)
    ).reset_index(level=0, drop=True)

    df1['Available_Balance'] = np.where(
        df1['Adjust_shortfall_Y/N'] == 'Y', 
        df1['cumulative_sum_12Months_OVERPAY'] + df1['cumulative_sum_12Months'],
        np.nan
    )

    df1['Offset_Shortfall_Y/N'] = np.where(
        (df1['Shortfall SG'] < 0) & (df1['Available_Balance'] > abs(df1['Shortfall SG'])), 'Y',
        np.where(
            (df1['Shortfall SG'] < 0) & (df1['cumulative_sum_12Months_OVERPAY'] > 0) & 
            (abs(df1['Available_Balance']) < abs(df1['Shortfall SG'])), 'P',
            'N'
        )
    )

    df1['Shortfall_Reduction'] = np.where(
        df1['Offset_Shortfall_Y/N'] == 'Y',
        df1['Shortfall SG'],
        np.where(df1['Offset_Shortfall_Y/N'] == 'P', 
                 -(abs(df1['Shortfall SG']) - abs(df1['Available_Balance'])),
                 np.where(df1['Offset_Shortfall_Y/N'] == 'N', 0, 0))
    )

    df1['Remaining_Shortfall_Balance'] = np.where(
        ((df1['Available_Balance'] <= 0) & (df1['Offset_Shortfall_Y/N'] == 'N')), df1['Shortfall SG'],
        np.where(
            ((df1['Available_Balance'] <= 0) & (df1['Offset_Shortfall_Y/N'] == 'P')), df1['Available_Balance'],
            np.where(
                ((df1['Offset_Shortfall_Y/N'] == 'N') & (df1['Shortfall SG'] < 0)), df1['Shortfall SG'],
                0
            )
        )
    )

    df1['One_Year_Prior'] = df1['Period_Ending'] - pd.DateOffset(years=1)

    return df1

offset = calculate_shortfall_offset(mergedData_Labour)
offset.to_csv('RollingShortfallOffset_output.csv', index=False)

# Commented out to test the new function
agg_methods = {
        'Full_Name': 'first',  
        'Line': 'first',
        'Description': 'first',
        'Hours/Value': 'sum',
        'Pay_Rate': 'mean',
        'Total': 'sum',
        'SG_Rate': 'mean',
        'FY_Q': 'first',
        'Financial_Year': 'first', 
       'Client Mapping' : 'first',
        'SW mapping' : 'first',
        'Client mapping - OTE' : 'sum',
        'SW Mapping - OTE' : 'sum',
        'SW Mapping - S&W' : 'sum',
        'Client Mapping - OTE SG Expected' : 'sum',
        'SW Map - OTE SG expected' : 'sum' , 
        'SW Map - S&W SG' : 'sum',
        'Payroll - actual SG paid' : 'sum', 
        'SCH - actual SG received' : 'sum'
    }



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
        'Line': 'first',
        'Description': 'first',
        'Hours/Value': 'sum',
        'Pay_Rate': 'mean',
        'Total': 'sum',
        'SG_Rate': 'mean',
        'FY_Q': 'first',
        'Period_Ending': 'first',
        'Financial_Year': 'first', 
       'Client Mapping' : 'first',
        'SW mapping' : 'first',
        'Client mapping - OTE' : 'sum',
        'SW Mapping - OTE' : 'sum',
        'SW Mapping - S&W' : 'sum',
        'Client Mapping - OTE SG Expected' : 'sum',
        'SW Map - OTE SG expected' : 'sum' , 
        'SW Map - S&W SG' : 'sum',
        'Payroll - actual SG paid' : 'sum', 
        'SCH - actual SG received' : 'sum'
    }

    # Ensure required columns exist in DataFrame before aggregating
    existing_columns = df.columns.intersection(agg_methods.keys())
    agg_methods = {col: agg_methods[col] for col in existing_columns}

    # Ensure the required group-by columns exist
    group_by_columns = ['QtrEMPLID', 'FY_Q_Label', 'Emp.Code', 'Combined_PayCode']
    #group_by_columns = ['QtrEMPLID', 'FY_Q_Label', 'Emp.Code', 'Pay_Number', 'PayCode']
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
    quarterly_summary['SW Mapping - OTE'] > quarterly_summary['MCB'],
    quarterly_summary['MCB'] * quarterly_summary['SG_Rate'], np.where(
       quarterly_summary['SW Mapping - OTE']  < quarterly_summary['MCB'], 
       quarterly_summary['SW Mapping - OTE'] * quarterly_summary['SG_Rate'],
       0 
        )
    )

    quarterly_summary['SW - Exepected Minimum SG'] = quarterly_summary['SW - Exepected Minimum SG'].astype(float).round(2)




    # Add Column Client - Expected Minimum SG

    quarterly_summary['Client - Exepected Minimum SG'] = np.where(
    quarterly_summary['Client mapping - OTE'] > quarterly_summary['MCB'],
    quarterly_summary['MCB'] * quarterly_summary['SG_Rate'], np.where(
       quarterly_summary['Client mapping - OTE']  < quarterly_summary['MCB'], 
       quarterly_summary['Client mapping - OTE'] * quarterly_summary['SG_Rate'],
       0 
        )
    )

    quarterly_summary['Client - Exepected Minimum SG'] = quarterly_summary['Client - Exepected Minimum SG'].astype(float).round(2)



    quarterly_summary['Above / Met cap'] = np.where(quarterly_summary['SW Mapping - OTE'] > quarterly_summary['MCB'], 'Above / met cap', 
        np.where(quarterly_summary['SW Mapping - OTE'] < quarterly_summary['MCB'], 'Below cap', "N/A"))
    

    

    quarterly_summary['Payroll - actual SG paid_CumSum'] = quarterly_summary.groupby(['Pay_Number'])['Payroll - actual SG paid'].cumsum()

    quarterly_summary['Client Mapping - OTE SG Expected_CumSum'] = quarterly_summary.groupby(['Pay_Number'])['Client Mapping - OTE SG Expected'].cumsum()

    quarterly_summary['SW Map - OTE SG expected_CumSum'] = quarterly_summary.groupby(['Pay_Number'])['SW Map - OTE SG expected'].cumsum()



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




combined_quarterly_summary['Line_ID'] = combined_quarterly_summary['Pay_Number'].astype(str) + '_' + combined_quarterly_summary['Line'].astype(str)


if 'SW - Final Comment' not in combined_quarterly_summary.columns:
    combined_quarterly_summary['Discrepancy 1 - SW Comment'] = ''




# def generate_comment(row):
#     if row['Client Mapping - OTE SG Expected'] == 0:
    
#         #return f"Client Mapping didn't make payment under this line {row['Line_ID']} Description: {row['Description']}"
#         return f"Client Mapping didn't classify line: {row['Line_ID']} as OTE"
#     elif row['SW Map - OTE SG expected'] == 0:
#         return f"SW Mapping didn't classify line: {row['Line_ID']} as OTE"
#     else:
#         return row.get('Discrepancy 1 - SW Comment', '')

def generate_comment(row):
    if row['SW mapping'] == 'OTE' and row['Client Mapping'] == 'N':
        return f"No payment under Client Mapping {row['Line_ID']} Description: {row['Description']}"
    
    
    elif row['Client Mapping'] == 'Y' and row['SW mapping'] != 'OTE':
        return f"Overpayment, SW Mapping didn't classify {row['Line_ID']} Description: {row['Description']} as OTE"
    
    else:
        return row.get('Discrepancy 1 - SW Comment', None)



    # Add column for Discrepancy 1 - SW Map Expected / Client Map
combined_quarterly_summary['Discrepancy 1 - SW Map Expected / Client Map'] = (combined_quarterly_summary['Client Mapping - OTE SG Expected'] - combined_quarterly_summary['SW Map - OTE SG expected']).round(2)

combined_quarterly_summary['Discrepancy 1 - SW Map Expected / Client Map'] = combined_quarterly_summary['Discrepancy 1 - SW Map Expected / Client Map'].astype(float).round(2)

    # Add column for Discrepancy 2 - Client Map - Expected Total SG

combined_quarterly_summary['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = (combined_quarterly_summary['Payroll - actual SG paid'] - combined_quarterly_summary['Client Mapping - OTE SG Expected']).round(2)
    
combined_quarterly_summary['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = combined_quarterly_summary['Discrepancy 2 -  Client Map Expected / Payroll Paid'].astype(float).round(2)
# Add column for Discrepancy 3 - SW Map Expected / Payroll paid
combined_quarterly_summary['Discrepancy 3 - SW Map Expected / Payroll paid'] = (combined_quarterly_summary['Payroll - actual SG paid'] - combined_quarterly_summary['SW Map - OTE SG expected']).round(2)

combined_quarterly_summary['Discrepancy 3 - SW Map Expected / Payroll paid'] = combined_quarterly_summary['Discrepancy 3 - SW Map Expected / Payroll paid'].astype(float).round(2)


combined_quarterly_summary['Discrepancy 1 - SW Comment'] = combined_quarterly_summary.apply(generate_comment, axis=1)



combined_quarterly_summary.to_csv('Payroll_Detail.csv', index=False)
# Problem is that its looking at the current data frame not the instance of the data frame that was used to create the grouped results

# If Payroll - actual SG paid_CumSum == 0 then SW - Final Comment = "SG paid is 0" in paynumber





# Need to create a dataframe that gets the total for quarter rather than the individual pay numbers
quarter_sum = combined_quarterly_summary









agg_methods = {\
        'Entity' : 'first',
        'Emp.Code' : 'first',
        'Full_Name': 'first',  
        #'Pay_Number': 'last',
        #'Line': 'first',
        'Hours/Value': 'sum',
        'Pay_Rate': 'mean',
        'Total': 'sum',
        'SG_Rate': 'mean',
        'FY_Q': 'first',
        'Financial_Year': 'first', 
        #'Client Mapping': 'first',
        #'SW mapping': 'first',
        'Client mapping - OTE': 'sum',
        'SW Mapping - OTE': 'sum',
        'SW Mapping - S&W': 'sum',
        'Client Mapping - OTE SG Expected': 'sum',
        'SW Map - OTE SG expected': 'sum', 
        'SW Map - S&W SG': 'sum',
        'Payroll - actual SG paid': 'sum', 
        'SCH - actual SG received': 'sum',
        'MCB' : 'first',
        # 'Payroll - actual SG paid_CumSum' : 'last',
        # 'Client Mapping - OTE SG Expected_CumSum' : 'last',
        # 'SW Map - OTE SG expected_CumSum' : 'last',
        #'Discrepancy 1 - SW Comment': 'first'

    }






# Check if required columns exist in DataFrame
group_by_columns = ['QtrEMPLID', 'Pay_Number']
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
    .groupby('Pay_Number')['Discrepancy 1 - SW Comment']
    .apply(lambda x: ' | '.join(x.dropna().astype(str)))
    .reset_index()
)



# Merge the concatenated comment back correctly
quarter_sum = quarter_sum.merge(comment_concat, on='Pay_Number', how='left')

# Rename the merged column to match your naming standard (optional)
# quarter_sum = quarter_sum.rename(columns={
#     'Discrepancy 1 - SW Comment': 'Discrepancy_1_SW_Comment_Concat'
# })




def generate_comment1(row):
    if row['Payroll - actual SG paid'] == 0:
        return f"No Super was paid under pay run number: {row['Pay_Number']}"
    elif row['Client Mapping - OTE SG Expected'] == 0:
        return f"Client Mapping didn't make payment under pay run number: {row['Pay_Number']}"
    else:
        return row.get('Discrepancy 2 - SW Comment', '')



def generate_comment2(row):
    
    if row['Payroll - actual SG paid'] == 0:
        return f"No Super was paid under pay run number: {row['Pay_Number']}"
    elif row['SW Map - OTE SG expected'] == 0:
        return f"SW Mapping didn't make payment under pay run number: {row['Pay_Number']}"
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
        #'Line': 'first',
        'Hours/Value': 'sum',
        'Pay_Rate': 'mean',
        'Total': 'sum',
        'SG_Rate': 'mean',
        'FY_Q': 'first',
        'Financial_Year': 'first', 
        #'Client Mapping': 'first',
        #'SW mapping': 'first',
        'Client mapping - OTE': 'sum',
        'SW Mapping - OTE': 'sum',
        'SW Mapping - S&W': 'sum',
        'Client Mapping - OTE SG Expected': 'sum',
        'SW Map - OTE SG expected': 'sum', 
        'SW Map - S&W SG': 'sum',
        'Payroll - actual SG paid': 'sum', 
        'SCH - actual SG received': 'sum',
        'MCB' : 'first',
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

    columns_to_drop = ['Pay_Number', 'Line', 'Hours/Value', 'Pay_Rate', 'Description', 'Total']
     # Drop unneeded columns if provided
   
    



    # Add second column for Client so there will be one sw and one client Above / Met Cap
    grouped_df['Above / Met cap (SW Map)'] = np.where(grouped_df['SW Mapping - OTE'] > grouped_df['MCB'], 'Above / met cap', 
        np.where(grouped_df['SW Mapping - OTE'] < grouped_df['MCB'], 'Below cap', "N/A"))
    
    grouped_df['Above / Met cap (Client Map)'] = np.where(grouped_df['Client mapping - OTE'] > grouped_df['MCB'], 'Above / met cap',
        np.where(grouped_df['Client mapping - OTE'] < grouped_df['MCB'], 'Below cap', "N/A"))
    

    
    

    # Add column for Discrepancy 1 - SW Map Expected / Client Map
    grouped_df['Discrepancy 1 - SW Map Expected / Client Map'] = (grouped_df['Client Mapping - OTE SG Expected'] - grouped_df['SW Map - OTE SG expected']).round(2)

    # Add column for Discrepancy 2 - Client Map - Expected Total SG

    grouped_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = (grouped_df['Payroll - actual SG paid'] - grouped_df['Client Mapping - OTE SG Expected']).round(2)
    
    # Add column for Discrepancy 3 - SW Map Expected / Payroll paid
    grouped_df['Discrepancy 3 - SW Map Expected / Payroll paid'] = (grouped_df['Payroll - actual SG paid'] - grouped_df['SW Map - OTE SG expected']).round(2)
    
    def generate_comment_Discrep_3 (row):
        if row['Discrepancy 1 - SW Map Expected / Client Map'] == row['Discrepancy 3 - SW Map Expected / Payroll paid']:
            return f"Mapping issue with pay run: {row['Pay_Number']} "
            #Description: {row['Description']}"
        
        elif row['Discrepancy 2 -  Client Map Expected / Payroll Paid'] == row['Discrepancy 3 - SW Map Expected / Payroll paid']:
            return f"Payroll issue with pay run: {row['Pay_Number']} "
        # Description: {row['Description']}"
        
        elif row['Discrepancy 1 - SW Map Expected / Client Map'] or row['Discrepancy 2 -  Client Map Expected / Payroll Paid'] != row['Discrepancy 3 - SW Map Expected / Payroll paid']:
            return f"unknown issue with pay run: {row['Pay_Number']} "
            # Description: {row['Description']}"

    
    grouped_df['Discrepancy 3 - SW Comment'] = grouped_df.apply(generate_comment_Discrep_3, axis=1)

    grouped_df = grouped_df.drop(columns=columns_to_drop, errors='ignore')  # ignore errors if columns don't exist

    column_order = ['Entity', 'QtrEMPLID', 'Emp.Code', 'Full_Name', 'SG_Rate', 'FY_Q',
       'Financial_Year', 'Client mapping - OTE', 'SW Mapping - OTE',
       'SW Mapping - S&W', 'Client Mapping - OTE SG Expected',
       'SW Map - OTE SG expected', 'SW Map - S&W SG',
       'Payroll - actual SG paid', 'SCH - actual SG received', 'MCB',
       'Above / Met cap (SW Map)',
       'Above / Met cap (Client Map)',
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
    #     r'No payment under Client Mapping|SW Mapping didn\'t classify line|Description:', 
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

    print(f"File saved: {filename}")
    return grouped_df







output_dir="output"
combined_result_df = SG_actual_Vs_SW_Map(quarter_sum)

print(combined_result_df.columns)


   



filename = os.path.join(output_dir, f"SG_Quarterly_BothEntities.csv")
combined_result_df.to_csv(filename, index=False)








import pandas as pd

def find_discrepant_paycodes_grouped(
    combined_result_df: pd.DataFrame,
    combined_quarterly_summary: pd.DataFrame,
    discrepancy_column: str,
    qtremplid_output_csv: str,
    grouped_output_csv: str
) -> pd.DataFrame:
    """
    Identifies discrepancies in SG Expected values, grouped by QtrEMPLID,
    and concatenates PayCode and Pay_Number into a single string per QtrEMPLID.

    Args:
        combined_result_df: DataFrame with discrepancy flags and QtrEMPLID.
        combined_quarterly_summary: DataFrame with SG expected values.
        discrepancy_column: Name of column used to identify discrepancies.
        qtremplid_output_csv: Path to save unique QtrEMPLIDs.
        grouped_output_csv: Path to save grouped PayCode/Pay_Number results.

    Returns:
        DataFrame grouped by QtrEMPLID with concatenated PayCode and Pay_Number entries.
    """

    # Step 1: Get QtrEMPLIDs with discrepancies
    flagged_ids = combined_result_df.loc[
        combined_result_df[discrepancy_column] != 0, 'QtrEMPLID'
    ].unique()

    # Step 2: Save flagged QtrEMPLIDs
    pd.DataFrame(flagged_ids, columns=['QtrEMPLID']).to_csv(qtremplid_output_csv, index=False)

    # Step 3: Filter summary by QtrEMPLID
    relevant_rows = combined_quarterly_summary[
        combined_quarterly_summary['QtrEMPLID'].isin(flagged_ids)
    ]

    # Step 4: Apply mismatch condition
    mismatches = relevant_rows[
        (relevant_rows['Client Mapping - OTE SG Expected'] -
         relevant_rows['SW Map - OTE SG expected']) != 0
    ]


    

    # Step 5: Create combined string: PayCode - Pay_Number
    #mismatches['Paycode_Entry'] = mismatches['PayCode'].astype(str) + ' - ' + mismatches['Pay_Number'].astype(str)

    mismatches['Paycode_Entry'] = mismatches['Pay_Number'].astype(str)
    # Step 6: Group by QtrEMPLID
    grouped = mismatches.groupby('QtrEMPLID')['Paycode_Entry'].apply(lambda x: ', '.join(x)).reset_index()

    # Step 7: Save result
    grouped.to_csv(grouped_output_csv, index=False)

    return grouped










def find_discrepant_paycodes_grouped1(
    combined_result_df: pd.DataFrame,
    quarter_sum: pd.DataFrame,
    discrepancy_column: str,
    qtremplid_output_csv: str,
    grouped_output_csv: str
) -> pd.DataFrame:
    """
    Identifies discrepancies in SG Expected values, grouped by QtrEMPLID,
    and concatenates PayCode and Pay_Number into a single string per QtrEMPLID.

    Args:
        combined_result_df: DataFrame with discrepancy flags and QtrEMPLID.
        combined_quarterly_summary: DataFrame with SG expected values.
        discrepancy_column: Name of column used to identify discrepancies.
        qtremplid_output_csv: Path to save unique QtrEMPLIDs.
        grouped_output_csv: Path to save grouped PayCode/Pay_Number results.

    Returns:
        DataFrame grouped by QtrEMPLID with concatenated PayCode and Pay_Number entries.
    """

    # Step 1: Get QtrEMPLIDs with discrepancies
    flagged_ids = combined_result_df.loc[
        combined_result_df[discrepancy_column] != 0, 'QtrEMPLID'
    ].unique()

    # Step 2: Save flagged QtrEMPLIDs
    pd.DataFrame(flagged_ids, columns=['QtrEMPLID']).to_csv(qtremplid_output_csv, index=False)

    # Step 3: Filter summary by QtrEMPLID
    # relevant_rows = combined_quarterly_summary[
    #     combined_quarterly_summary['QtrEMPLID'].isin(flagged_ids)
    # ]

    relevant_rows = quarter_sum[quarter_sum['QtrEMPLID'].isin(flagged_ids)]

    # Step 4: Apply mismatch condition
    mismatches = relevant_rows[
        (relevant_rows['Payroll - actual SG paid'] -
         relevant_rows['Client Mapping - OTE SG Expected']) != 0
    ]

       

    # Step 5: Create combined string: PayCode - Pay_Number
   # mismatches['Paycode_Entry'] = mismatches['PayCode'].astype(str) + ' - ' + mismatches['Pay_Number'].astype(str)
    mismatches['Paycode_Entry'] = mismatches['Pay_Number'].astype(str)
    # Step 6: Group by QtrEMPLID
    grouped = mismatches.groupby('QtrEMPLID')['Paycode_Entry'].apply(lambda x: ', '.join(x)).reset_index()

    # Step 7: Save result
    grouped.to_csv(grouped_output_csv, index=False)

    return grouped


def find_discrepant_paycodes_grouped2(
    combined_result_df: pd.DataFrame,
    quarter_sum: pd.DataFrame,
    discrepancy_column: str,
    qtremplid_output_csv: str,
    grouped_output_csv: str
) -> pd.DataFrame:
    """
    Identifies discrepancies in SG Expected values, grouped by QtrEMPLID,
    and concatenates PayCode and Pay_Number into a single string per QtrEMPLID.

    Args:
        combined_result_df: DataFrame with discrepancy flags and QtrEMPLID.
        combined_quarterly_summary: DataFrame with SG expected values.
        discrepancy_column: Name of column used to identify discrepancies.
        qtremplid_output_csv: Path to save unique QtrEMPLIDs.
        grouped_output_csv: Path to save grouped PayCode/Pay_Number results.

    Returns:
        DataFrame grouped by QtrEMPLID with concatenated PayCode and Pay_Number entries.
    """

    # Step 1: Get QtrEMPLIDs with discrepancies
    flagged_ids = combined_result_df.loc[
        combined_result_df[discrepancy_column] != 0, 'QtrEMPLID'
    ].unique()

    # Step 2: Save flagged QtrEMPLIDs
    pd.DataFrame(flagged_ids, columns=['QtrEMPLID']).to_csv(qtremplid_output_csv, index=False)

    # Step 3: Filter summary by QtrEMPLID
    relevant_rows = combined_quarterly_summary[
        combined_quarterly_summary['QtrEMPLID'].isin(flagged_ids)
    ]

    # Step 4: Apply mismatch condition
    mismatches = relevant_rows[
        (relevant_rows['Payroll - actual SG paid'] -
         relevant_rows['SW Map - OTE SG expected']) != 0
    ]


    # Step 5: Create combined string: PayCode - Pay_Number
    mismatches['Paycode_Entry'] = mismatches['Combined_PayCode'].astype(str) + ' - ' + mismatches['Pay_Number'].astype(str)

    # Step 6: Group by QtrEMPLID
    grouped = mismatches.groupby('QtrEMPLID')['Paycode_Entry'].apply(lambda x: ', '.join(x)).reset_index()

    # Step 7: Save result
    grouped.to_csv(grouped_output_csv, index=False)

    return grouped



grouped_results = find_discrepant_paycodes_grouped(
    combined_result_df,
    combined_quarterly_summary,
    discrepancy_column='Discrepancy 1 - SW Map Expected / Client Map',
    qtremplid_output_csv='Discp1_QtrEMPLIDs.csv',
    grouped_output_csv='Discp1_Grouped_Paycode_Entries.csv'
)


grouped_results1 = find_discrepant_paycodes_grouped1(
    combined_result_df,
    quarter_sum,
    discrepancy_column='Discrepancy 2 -  Client Map Expected / Payroll Paid',
    qtremplid_output_csv='Discp2_QtrEMPLIDs.csv',
    grouped_output_csv='Discp2_Grouped_Paycode_Entries.csv'
)

grouped_results2 = find_discrepant_paycodes_grouped2(
    combined_result_df,
    quarter_sum,
    discrepancy_column='Discrepancy 3 - SW Map Expected / Payroll paid',
    qtremplid_output_csv='Discp3_QtrEMPLIDs.csv',
    grouped_output_csv='Discp3_Grouped_Paycode_Entries.csv'
)




# 29/04/25 - Next step is to join the grouped results with the original DataFrame in a new column called Discrepancy 1 - SW Comment


combined_result_df = combined_result_df.merge(grouped_results, on='QtrEMPLID', how='left')
combined_result_df.rename(columns={'Paycode_Entry': 'Discrepancy 1 - Source'}, inplace=True)


combined_result_df = combined_result_df.merge(grouped_results1, on='QtrEMPLID', how='left')
combined_result_df.rename(columns={'Paycode_Entry': 'Discrepancy 2 - Source'}, inplace=True)

combined_result_df = combined_result_df.merge(grouped_results2, on='QtrEMPLID', how='left')
combined_result_df.rename(columns={'Paycode_Entry': 'Discrepancy 3 - Source'}, inplace=True)



# combined_result_df['Discrepancy 1 - SW Map Expected / Client Map'] = combined_result_df['Discrepancy 1 - SW Map Expected / Client Map'].round(2)
# combined_result_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = combined_result_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'].round(2)
# combined_result_df['Discrepancy 3 - SW Map Expected / Payroll paid'] = combined_result_df['Discrepancy 3 - SW Map Expected / Payroll paid'].round(2)




dataframes = [combined_result_df, quarter_sum, combined_quarterly_summary]

combined_result_df.to_csv('combined_result_with_comments.csv', index=False)




sheet_names = ['Result', 'Quarterly Summary', 'Payroll Detail']


output_excel = 'client_payroll_analysis.xlsx'


# Write each DataFrame to a separate sheet
with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
    for df, sheet_name in zip(dataframes, sheet_names):
        df.to_excel(writer, sheet_name=sheet_name, index=False)


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


# Where QtrEMPLID is in the list of unique QtrEMPLID for Discrepancy 1 find rows where combined_quarterly_summary['Client Mapping - OTE SG Expected'] - combined_quarterly_summary['SW Map - OTE SG expected'] != 0
# and return the values in columns PayCode and Pay_Number



combined_quarterly_summary_Discp1 = combined_quarterly_summary[combined_quarterly_summary['QtrEMPLID'].isin(Discp1_unique_QtrEMPLID)]



