import sys
print(sys.executable)

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
                    0
                )
            )
        )
    )
    
    
    

    
    # Define PayCode lists
    OTE_paycodesBigBoats = [
        "NORMAL", "CASBNS", "PH", "AL", "SL", "TAFE", "WCOMP-EX", "HRSBNS", 
        "AL-CASHO", "BEREAVE", "PL-VACC", "VEHICLE", "BACK", "MVGARTH", "BONUS"
    ]
    
    OTE_paycodesSW = [
        "NORMAL", "CASBNS", "PH", "AL", "SL", "HRSBNS", "AL-CASHO", "BEREAVE", 
        "PL-VACC", "LOADING", "MEAL4", "BACK", "MVGARTH", "LOAD", "MEAL", "BONUS"
    ]


    # Get all unique values from both lists
    unique_paycodes = list(set(OTE_paycodesBigBoats + OTE_paycodesSW))

    # Print the result
    print('unique_paycodes')
    print(unique_paycodes)


    merged_data['Client Mapping'] = np.where(
         merged_data['PayCode'].isin(OTE_paycodesBigBoats),
        'Y',
        'N'
    )

    merged_data['SW mapping'] = np.where(
        merged_data['PayCode'].isin(OTE_paycodesSW),
        'OTE',
        'S&W'
    )
    

    
    # Calculate OTE amounts for Client and SW OTE mappings
    merged_data['Client mapping - OTE'] = np.where(
        merged_data['PayCode'].isin(OTE_paycodesBigBoats),
        merged_data['Total'],
        0
    )
    
    merged_data['SW Mapping - OTE'] = np.where(
        merged_data['PayCode'].isin(OTE_paycodesSW),
        merged_data['Total'],
        0
    )

    merged_data['SW Mapping - S&W'] = np.where(
        merged_data['PayCode'].isin(OTE_paycodesSW),
        0,
        merged_data['Total']
    )

    # Test 28/04/25
    # merged_data['Client Mapping - S&W'] = np.where(
    #     merged_data['PayCode'].isin(OTE_paycodesBigBoats),
    #     0,
    #     merged_data['Total']
    # )

    
    # Calculate SG Actuals and Expected
    merged_data['Client Mapping - OTE SG Expected'] = np.where(
        merged_data['PayCode'].isin(OTE_paycodesBigBoats),
        merged_data['Total'] * merged_data['SG_Rate'],
        0
    )
    
    merged_data['SW Map - OTE SG expected'] = np.where(
        merged_data['PayCode'].isin(OTE_paycodesSW),
        merged_data['Total'] * merged_data['SG_Rate'],
        0
    )



    merged_data['SW Map - S&W SG'] = merged_data['SW Mapping - S&W'] * merged_data['SG_Rate']

   

    super_codes = ['8', '9']

    merged_data['Payroll - actual SG paid'] = np.where(
        merged_data['PayCode'].isin(super_codes),
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
        'Emp.Code', 'Full_Name', 'Pay_Number', 'Line', 'PayCode', 'Description_x', 'Hours/Value', 
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
    group_by_columns = ['QtrEMPLID', 'FY_Q_Label', 'Emp.Code', 'PayCode']
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



    # Add Column Client - Expected Minimum SG

    quarterly_summary['Client - Exepected Minimum SG'] = np.where(
    quarterly_summary['Client mapping - OTE'] > quarterly_summary['MCB'],
    quarterly_summary['MCB'] * quarterly_summary['SG_Rate'], np.where(
       quarterly_summary['Client mapping - OTE']  < quarterly_summary['MCB'], 
       quarterly_summary['Client mapping - OTE'] * quarterly_summary['SG_Rate'],
       0 
        )
    )

    quarterly_summary['Above / Met cap'] = np.where(quarterly_summary['SW Mapping - OTE'] > quarterly_summary['MCB'], 'Above / met cap', 
        np.where(quarterly_summary['SW Mapping - OTE'] < quarterly_summary['MCB'], 'Below cap', "N/A"))
    

    # Add column for Discrepancy 1 - SW Map Expected / Client Map
    quarterly_summary['Discrepancy 1 - SW Map Expected / Client Map'] = (quarterly_summary['Client - Exepected Minimum SG'] - quarterly_summary['SW - Exepected Minimum SG']).round(0)

    # Add column for Discrepancy 2 - Client Map - Expected Total SG

    quarterly_summary['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = (quarterly_summary['Payroll - actual SG paid'] - quarterly_summary['Client Mapping - OTE SG Expected']).round(0)
    
    # Add column for Discrepancy 3 - SW Map Expected / Payroll paid
    quarterly_summary['Discrepany 3 - SW Map Expected / Payroll paid'] = (quarterly_summary['Payroll - actual SG paid'] - quarterly_summary['SW Map - OTE SG expected']).round(0)
    
    quarterly_summary['SW Comment - Discrepancy 1'] = ""
    quarterly_summary['SW Comment - Discrepancy 2'] = ""
    quarterly_summary['SW Comment - Discrepancy 3'] = ""
    quarterly_summary['SW - Final Comment'] = ""



    
# # # Adding the new column 
# # QTR_Results["SW Comment - Discrepancy 1"] = np.where(
# #     QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] == 0, "No discrepancy",
# #     np.where(
# #         QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] == QTR_Results["SW Map expected Additional SG"], "Missing additional super (0.5%)",
# #         np.where(
# #             QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] >= 1, "Under - mapping config issue",
# #             np.where(
# #                 QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] <= -1, "Over - mapping config difference",
# #                 np.where(
# #                     (-1 < QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"]) & (QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] < 1), "No discrepancy",
# #                     None
# #                 )
# #             )
# #         )
# #     )
# # )


# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 22.")


# # # Step 23: Adding Discrepency 2 comment column

# # QTR_Results["SW Comment - Discrepancy 2"] = np.where(
# #     (QTR_Results["Discrepancy 2 - FLUOR System Calc"] < 1) & 
# #     (QTR_Results["Discrepancy 2 - FLUOR System Calc"] > -1), "No discrepancy",
# #     np.where(
# #         (QTR_Results["Discrepancy 2 - FLUOR System Calc"] != 0) & 
# #         ((QTR_Results["FLOUR - OTE"] * 
# #           (QTR_Results["SG Rate"] + QTR_Results["Additional Super Rate"]) - 
# #           QTR_Results["Payroll Super"]) < 1) & 
# #         ((QTR_Results["FLOUR - OTE"] * 
# #           (QTR_Results["SG Rate"] + QTR_Results["Additional Super Rate"]) - 
# #           QTR_Results["Payroll Super"]) > -1), "Not capping",
# #         np.where(
# #             QTR_Results["FLOUR Map - Expected Total SG"] == 
# #             QTR_Results["Discrepancy 2 - FLUOR System Calc"], "No payroll super",
# #             np.where(
# #                 QTR_Results["Discrepancy 2 - FLUOR System Calc"] >= 1, "Under - System calc issue",
# #                 np.where(
# #                     QTR_Results["Discrepancy 2 - FLUOR System Calc"] <= -1, "Over - System calc difference",
# #                     None
# #                 )
# #             )
# #         )
# #     )
# # )

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 23.")


# # # Step 24: Adding Discrepency 3 comment column

# # QTR_Results["SW Comment - Discrepancy 3"] = np.where(
# #     QTR_Results["Discrepancy 3 - FLUOR Paid Calc"] >= 1, "Under - Actual paid issue",
# #     np.where(
# #         QTR_Results["Discrepancy 3 - FLUOR Paid Calc"] <= -1, "Over - Actual paid difference",
# #         np.where(
# #             QTR_Results["Discrepancy 3 - FLUOR Paid Calc"] < -1, "No discrepancy",
# #             np.where(
# #                 QTR_Results["Discrepancy 3 - FLUOR Paid Calc"] > -1, "No discrepancy",
# #                 None
# #             )
# #         )
# #     )
# # )

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 24.")


# # # Step 25: Adding Discrepency 4 comment column

# # QTR_Results["SW Comment - Discrepancy 4"] = np.where(
# #     (QTR_Results["SW Comment - Discrepancy 1"] == "No discrepancy") & 
# #     (QTR_Results["SW Comment - Discrepancy 3"] == "No discrepancy") & 
# #     (QTR_Results["SW Comment - Discrepancy 2"] == "No super"), "No Super",
# #     np.where(
# #         QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] == 
# #         QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"], QTR_Results["SW Comment - Discrepancy 1"],
# #         np.where(
# #             (QTR_Results["SW Comment - Discrepancy 1"] == "No discrepancy") & 
# #             (QTR_Results["Discrepancy 2 - FLUOR System Calc"] == QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"]),
# #             QTR_Results["SW Comment - Discrepancy 2"],
# #             np.where(
# #                 (QTR_Results["SW Comment - Discrepancy 1"] != "No discrepancy") & 
# #                 (QTR_Results["SW Comment - Discrepancy 2"] != "No discrepancy") & 
# #                 (QTR_Results["SW Comment - Discrepancy 3"] == "No discrepancy"),
# #                 QTR_Results["SW Comment - Discrepancy 1"] + " & " + QTR_Results["SW Comment - Discrepancy 2"],
# #                 np.where(
# #                     (QTR_Results["SW Comment - Discrepancy 1"] != "No discrepancy") & 
# #                     (QTR_Results["SW Comment - Discrepancy 2"] == "No discrepancy") & 
# #                     (QTR_Results["SW Comment - Discrepancy 3"] == "No discrepancy"),
# #                     QTR_Results["SW Comment - Discrepancy 1"],
# #                     np.where(
# #                         (QTR_Results["SW Comment - Discrepancy 1"] == "No discrepancy") & 
# #                         (QTR_Results["SW Comment - Discrepancy 2"] == "No discrepancy") & 
# #                         (QTR_Results["SW Comment - Discrepancy 3"] != "No discrepancy"),
# #                         QTR_Results["SW Comment - Discrepancy 3"],
# #                         np.where(
# #                             (QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"] >= 1), "Under",
# #                             np.where(
# #                                 (QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"] <= -1), "Over",
# #                                 np.where(
# #                                     (-1 < QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"]) & 
# #                                     (QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"] < 1), "No discrepancy",
# #                                     None
# #                                 )
# #                             )
# #                         )
# #                     )
# #                 )
# #             )
# #         )
# #     )
# # )

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 25.")




    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define output file path
    filename = os.path.join(output_dir, f"Quarterly_payroll_data_{file_suffix}.csv")

    # Save to CSV
    quarterly_summary.to_csv(filename, index=False)

    print(f"File saved: {filename}")
    return quarterly_summary



quarterly_summary_LAB = aggregate_quarterly_data(mergedData_Labour)
quarterly_summary_OFF = aggregate_quarterly_data(mergedData_Offshore, file_suffix="OFFSHORE")

combined_quarterly_summary = pd.concat([quarterly_summary_OFF, quarterly_summary_LAB], ignore_index=True)


def SG_actual_Vs_SW_Map(df, output_dir="output", file_suffix="LABOUR"):
    # Define aggregation methods
    agg_methods = {\
        'Emp.Code' : 'first',
        'Full_Name': 'first',  
        'Pay_Number': 'first',
        'Line': 'first',
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
        'SCH - actual SG received': 'sum',
        'MCB' : 'first',

    }

    # Check if required columns exist in DataFrame
    group_by_columns = ['QtrEMPLID']
    missing_cols = [col for col in group_by_columns if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Perform aggregation
    grouped_df = df.groupby(group_by_columns).agg(agg_methods).reset_index()


    columns_to_drop = ['Pay_Number', 'Line', 'Hours/Value', 'Pay_Rate', 'Description', 'Total', 'Client Mapping', 'SW mapping']

     # Drop unneeded columns if provided
   
    grouped_df = grouped_df.drop(columns=columns_to_drop, errors='ignore')  # ignore errors if columns don't exist




    grouped_df['Above / Met cap'] = np.where(grouped_df['SW Mapping - OTE'] > grouped_df['MCB'], 'Above / met cap', 
        np.where(grouped_df['SW Mapping - OTE'] < grouped_df['MCB'], 'Below cap', "N/A"))
    

    # Add column for Discrepancy 1 - SW Map Expected / Client Map
    grouped_df['Discrepancy 1 - SW Map Expected / Client Map'] = (grouped_df['Client Mapping - OTE SG Expected'] - grouped_df['SW Map - OTE SG expected']).round(0)

    # Add column for Discrepancy 2 - Client Map - Expected Total SG

    grouped_df['Discrepancy 2 -  Client Map Expected / Payroll Paid'] = (grouped_df['Payroll - actual SG paid'] - grouped_df['Client Mapping - OTE SG Expected']).round(0)
    
    # Add column for Discrepancy 3 - SW Map Expected / Payroll paid
    grouped_df['Discrepany 3 - SW Map Expected / Payroll paid'] = (grouped_df['Payroll - actual SG paid'] - grouped_df['SW Map - OTE SG expected']).round(0)
    
    grouped_df['SW Comment - Discrepancy 1'] = ""
    grouped_df['SW Comment - Discrepancy 2'] = ""
    grouped_df['SW Comment - Discrepancy 3'] = ""
    grouped_df['SW - Final Comment'] = ""



    # Commented out 29/04/2025
    # grouped_df['Payroll_Vs_SW_Expected_Min_SG'] = grouped_df['Payroll - actual SG paid'] - grouped_df['SW - Exepected Minimum SG']

    # grouped_df['Payroll_Vs_Client_Expected_Min_SG'] = grouped_df['Payroll - actual SG paid'] - grouped_df['Client - Exepected Minimum SG']

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define output file path
    #filename = os.path.join(output_dir, f"SG_actual_Vs_SW_Map_{file_suffix}.csv")
    filename = os.path.join(output_dir, f"SG_Quarterly_{file_suffix}.csv")
    # Save to CSV
    grouped_df.to_csv(filename, index=False)

    print(f"File saved: {filename}")
    return grouped_df

# Call the function with your DataFrame
result_df_OFF = SG_actual_Vs_SW_Map(quarterly_summary_OFF, file_suffix='OFFSHORE')
result_df_OFF['Entity'] = 'OFFSHORE'
result_df_LAB = SG_actual_Vs_SW_Map(quarterly_summary_LAB, file_suffix='LABOUR')
result_df_LAB['Entity'] = 'LABOUR'
# Combine the results into a single DataFrame
output_dir="output"

combined_result_df = pd.concat([result_df_OFF, result_df_LAB], ignore_index=True)

print(combined_result_df.columns)

column_order = ['Entity', 'QtrEMPLID', 'Emp.Code', 'Full_Name', 'SG_Rate', 'FY_Q',
       'Financial_Year', 'Client mapping - OTE', 'SW Mapping - OTE',
       'SW Mapping - S&W', 'Client Mapping - OTE SG Expected',
       'SW Map - OTE SG expected', 'SW Map - S&W SG',
       'Payroll - actual SG paid', 'SCH - actual SG received', 'MCB',
       'Above / Met cap', 'Discrepancy 1 - SW Map Expected / Client Map',
       'Discrepancy 2 -  Client Map Expected / Payroll Paid',
       'Discrepany 3 - SW Map Expected / Payroll paid',
       'SW Comment - Discrepancy 1', 'SW Comment - Discrepancy 2',
       'SW Comment - Discrepancy 3', 'SW - Final Comment']

        
    # Reorder the DataFrame columns
combined_result_df = combined_result_df[column_order]



filename = os.path.join(output_dir, f"SG_Quarterly_BothEntities.csv")
combined_result_df.to_csv(filename, index=False)




# def find_discrepant_paycodes(
#     combined_result_df: pd.DataFrame,
#     combined_quarterly_summary: pd.DataFrame,
#     discrepancy_column: str,
#     qtremplid_output_csv: str,
#     paycode_output_csv: str
# ) -> pd.DataFrame:
#     """
#     Identifies and saves discrepancies in SG Expected values for QtrEMPLIDs flagged
#     by a given discrepancy column. Outputs both the unique QtrEMPLIDs and mismatched
#     PayCode/Pay_Number entries to CSV.

#     Args:
#         combined_result_df: DataFrame with discrepancy flags and QtrEMPLID.
#         combined_quarterly_summary: DataFrame with SG expected values.
#         discrepancy_column: Column name for discrepancy check (non-zero).
#         qtremplid_output_csv: Path to save unique QtrEMPLIDs CSV.
#         paycode_output_csv: Path to save mismatched PayCode/Pay_Number CSV.

#     Returns:
#         A DataFrame of mismatched PayCode and Pay_Number.
#     """

#     # Step 1: Get unique QtrEMPLIDs with discrepancies
#     flagged_ids = combined_result_df.loc[
#         combined_result_df[discrepancy_column] != 0, 'QtrEMPLID'
#     ].unique()

#     # Step 2: Save the QtrEMPLIDs to CSV
#     pd.DataFrame(flagged_ids, columns=['QtrEMPLID']).to_csv(qtremplid_output_csv, index=False)

#     # Step 3: Filter combined_quarterly_summary for those QtrEMPLIDs
#     relevant_rows = combined_quarterly_summary[
#         combined_quarterly_summary['QtrEMPLID'].isin(flagged_ids)
#     ]

#     # Step 4: Find mismatches in SG expected values
#     mismatches = relevant_rows[
#         (relevant_rows['Client Mapping - OTE SG Expected'] -
#          relevant_rows['SW Map - OTE SG expected']) != 0
#     ]

#     # Step 5: Select PayCode and Pay_Number
#     result_df = mismatches[['QtrEMPLID', 'PayCode', 'Pay_Number']]

#     # Concat the Paycode rows with Pay_Number rows.  Group in the same Cell where QtrEMPLID is the same

#     # Step 6: Save result to CSV
#     result_df.to_csv(paycode_output_csv, index=False)

#     return result_df



# discp1_results = find_discrepant_paycodes(
#     combined_result_df,
#     combined_quarterly_summary,
#     discrepancy_column='Discrepancy 1 - SW Map Expected / Client Map',
#     qtremplid_output_csv='Discp1_QtrEMPLIDs.csv',
#     paycode_output_csv='Discp1_Paycode_Mismatches.csv'
# )

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
    mismatches['Paycode_Entry'] = mismatches['PayCode'].astype(str) + ' - ' + mismatches['Pay_Number'].astype(str)

    # Step 6: Group by QtrEMPLID
    grouped = mismatches.groupby('QtrEMPLID')['Paycode_Entry'].apply(lambda x: ', '.join(x)).reset_index()

    # Step 7: Save result
    grouped.to_csv(grouped_output_csv, index=False)

    return grouped



def find_discrepant_paycodes_grouped1(
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
        (relevant_rows['Payroll - actual SG paid'] -
         relevant_rows['Client Mapping - OTE SG Expected']) != 0
    ]

       

    # Step 5: Create combined string: PayCode - Pay_Number
    mismatches['Paycode_Entry'] = mismatches['PayCode'].astype(str) + ' - ' + mismatches['Pay_Number'].astype(str)

    # Step 6: Group by QtrEMPLID
    grouped = mismatches.groupby('QtrEMPLID')['Paycode_Entry'].apply(lambda x: ', '.join(x)).reset_index()

    # Step 7: Save result
    grouped.to_csv(grouped_output_csv, index=False)

    return grouped


def find_discrepant_paycodes_grouped2(
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
        (relevant_rows['Payroll - actual SG paid'] -
         relevant_rows['SW Map - OTE SG expected']) != 0
    ]


    # Step 5: Create combined string: PayCode - Pay_Number
    mismatches['Paycode_Entry'] = mismatches['PayCode'].astype(str) + ' - ' + mismatches['Pay_Number'].astype(str)

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
    combined_quarterly_summary,
    discrepancy_column='Discrepancy 2 -  Client Map Expected / Payroll Paid',
    qtremplid_output_csv='Discp2_QtrEMPLIDs.csv',
    grouped_output_csv='Discp2_Grouped_Paycode_Entries.csv'
)

grouped_results2 = find_discrepant_paycodes_grouped2(
    combined_result_df,
    combined_quarterly_summary,
    discrepancy_column='Discrepany 3 - SW Map Expected / Payroll paid',
    qtremplid_output_csv='Discp3_QtrEMPLIDs.csv',
    grouped_output_csv='Discp3_Grouped_Paycode_Entries.csv'
)




# 29/04/25 - Next step is to join the grouped results with the original DataFrame in a new column called Discrepancy 1 - SW Comment


combined_result_df = combined_result_df.merge(grouped_results, on='QtrEMPLID', how='left')
combined_result_df.rename(columns={'Paycode_Entry': 'Discrepancy 1 - SW Comment'}, inplace=True)


combined_result_df = combined_result_df.merge(grouped_results1, on='QtrEMPLID', how='left')
combined_result_df.rename(columns={'Paycode_Entry': 'Discrepancy 2 - SW Comment'}, inplace=True)

combined_result_df = combined_result_df.merge(grouped_results2, on='QtrEMPLID', how='left')
combined_result_df.rename(columns={'Paycode_Entry': 'Discrepancy 3 - SW Comment'}, inplace=True)

combined_result_df.to_csv('combined_result_with_comments.csv', index=False)



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
Discprepancy_3 = combined_result_df[combined_result_df['Discrepany 3 - SW Map Expected / Payroll paid'] != 0]

# get unique QtrEMPLID for Discrepancy 1
Discp1_unique_QtrEMPLID = Discprepancy_1['QtrEMPLID'].unique()   

pd.DataFrame(Discp1_unique_QtrEMPLID, columns=['QtrEMPLID']).to_csv('Discp1_unique_QtrEMPLID.csv', index=False)


# Where QtrEMPLID is in the list of unique QtrEMPLID for Discrepancy 1 find rows where combined_quarterly_summary['Client Mapping - OTE SG Expected'] - combined_quarterly_summary['SW Map - OTE SG expected'] != 0
# and return the values in columns PayCode and Pay_Number



combined_quarterly_summary_Discp1 = combined_quarterly_summary[combined_quarterly_summary['QtrEMPLID'].isin(Discp1_unique_QtrEMPLID)]





# Client Mapping - OTE SG Expected	SW Map - OTE SG expected


    
    # Add more commentary logic as needed for other discrepancies

    # Ensure the output directory exists
    # os.makedirs(output_dir, exist_ok=True)

    # # Define output file path
    # filename = os.path.join(output_dir, "commentary_output.csv")
    
    # # Save to CSV
    # df.to_csv(filename, index=False)

    # print(f"Commentary file saved: {filename}")
    
    # return df




    # Add more commentary logic as needed for other discrepancies

    # Ensure the output directory exists
    # os.makedirs(output_dir, exist_ok=True)

    # # Define output file path
    # filename = os.path.join(output_dir, "commentary_output.csv")
    
    # # Save to CSV
    # df.to_csv(filename, index=False)

    # print(f"Commentary file saved: {filename}")
    
    # return df


# # Payroll_Period_Code =  merged_data
# # # Clean and convert 'Emp Code' column (keeping leading zeros and formatting with 5 digits)
# # Payroll_Period_Code['Emp Code'] = Payroll_Period_Code['Emp Code'] \
# #     .astype(str) \
# #     .str.strip() \
# #     .replace('', float('NaN')) \
# #     .dropna() \
# #     .apply(lambda x: x.zfill(7))  # Adds leading zeros to ensure 5 digits

# # print('Payroll_Period_Code head: ')
# # print(Payroll_Period_Code.head)

# # print('Payroll Period Code: ')
# # print(Payroll_Period_Code.columns)

# # def count_rows(df):
# #     """
# #     Counts the number of rows in a DataFrame.

# #     Parameters:
# #     df (pd.DataFrame): The DataFrame to count rows for.

# #     Returns:
# #     int: The number of rows in the DataFrame.
# #     """
# #     return len(df)

# print('QTR Results Labour columns: ')
# print(QTR_results_Labour.columns)

# # # Step 1: Group rows and sum 

# QTR_results_Offshore = QTR_results_Offshore[[
#     'Emp.Code', 'PayCode', 'Period_Ending', 'Full_Name', 'Pay_Number',
#     'Line', 'Description_x', 'Hours/Value', 'Pay_Rate', 'Quarterly_Total',
#     # 'Cost_Centre', 'Emp_Group', 'PayCode_Type', 'Description_y', 'Type',
#     # 'Tax_Status_Income_Category', 'Formula', 'Value', 'Fixed_Variable',
#     # 'Tax_Cert_Status', 'Min_$', 'Max_$', 'Min_Qty', 'Max_Qty',
#     # 'Super_on_Pay_Advice', 'Show_rate_on_Pay_Advice',
#     # 'Show_YTD_on_Pay_Advice', 'Allow_Data_Entry',
#     # 'Multiple_G_L_Dissections', 'Show_on_Pay_Advice',
#     # 'Include_in_SG_Threshold', 'Frequency', 'Super_for_Casuals_Under_18',
#     # 'Reduce_Hours', 'Inactive', 'Calculation_Table', 'WCOMP', 'Days_Date',
#     # 'Back_Pay', 'Count_from', 'Disperse_over_Cost_Centres',
#     'Quarterly_Value_Maximum', 'Monthly_Threshold', 'SG_Rate',
#     'BigBoats - SG Actuals', 'SW Map - OTE SG expected', 'Super_Diff'
# ]].copy()




# # # # Step 2:  Add Column MCB
# # 2020 - 2021 - $57 090

# QTR_results_Offshore['MCB'] = np.where(
#     QTR_results_Offshore['Period_Ending'].dt.year == 2021, 58920, # Need to confirm with Paul or Ollie if this is correct
#     np.where(
#         QTR_results_Offshore['Period_Ending'].dt.year == 2022, 58920,
#         np.where(
#             QTR_results_Offshore['Period_Ending'].dt.year == 2023, 60220,
#             np.where(QTR_results_Offshore['Period_Ending'].dt.year == 2024, 62270, 0)
#         )
#     )
# )


# # row_count = count_rows(Payroll_Period_Code)
# # print(f"The DataFrame has {row_count} rows after Step 2.")



# # # # Step 3: Add Column SW Map - expected Minimum SG
# # # Payroll_Period_Code['SW Map - expected Minimum SG'] = Payroll_Period_Code.apply(
# # #   lambda row:
# # #   row['MCB'] * row['SG Rate'] if row['SW - OTE'] > row['MCB'] else
# # #   row['SW - OTE'] * row['SG Rate'] if row['SW - OTE'] < row['MCB'] else
# # #   0,
# # #   axis=1
# # # )

# # # Step 3: Add Column SW Map - expected Minimum SG
# # Payroll_Period_Code['SW Map - expected Minimum SG'] = np.where(
# #     Payroll_Period_Code['SW - OTE'] > Payroll_Period_Code['MCB'],
# #     Payroll_Period_Code['MCB'] * Payroll_Period_Code['SG Rate'], np.where(
# #        Payroll_Period_Code['SW - OTE'] < Payroll_Period_Code['MCB'], 
# #        Payroll_Period_Code['SW - OTE'] * Payroll_Period_Code['SG Rate'],
# #        0 
# #     )
# # )


# # row_count = count_rows(Payroll_Period_Code)
# # print(f"The DataFrame has {row_count} rows after Step 3.")



# # # Step 4: Add Column SW Map - expected Additional SG
# # # Payroll_Period_Code['SW Map expected Additional SG'] = Payroll_Period_Code.apply(
# # #   lambda row:
# # #   row['MCB'] * row['Additional Super Rate'] if row['SW - OTE'] > row['MCB'] else
# # #   row['SW - OTE'] * row['Additional Super Rate'] if row['SW - OTE'] < row['MCB'] else
# # #   0,
# # #   axis=1
# # #   )





# # Payroll_Period_Code['SW Map - total expected SG'] = Payroll_Period_Code['SW Map - expected Minimum SG'] +  Payroll_Period_Code['SW Map expected Additional SG']

# # row_count = count_rows(Payroll_Period_Code)
# # print(f"The DataFrame has {row_count} rows after Step 5.")



# # # Step 6: Add Column FLOUR Map - Expected Minimum SG
# # Payroll_Period_Code['FLOUR Map - expected Minimum SG'] = np.where(
# #   Payroll_Period_Code['FLOUR - OTE'] > Payroll_Period_Code['MCB'], 
# #     Payroll_Period_Code['MCB'] * Payroll_Period_Code['SG Rate'],
# #     np.where(
# #       Payroll_Period_Code['FLOUR - OTE'] < Payroll_Period_Code['MCB'],
# #       Payroll_Period_Code['FLOUR - OTE'] * Payroll_Period_Code['SG Rate'],
# #       0
# #     )
# # )

# # row_count = count_rows(Payroll_Period_Code)
# # print(f"The DataFrame has {row_count} rows after Step 6.")

# # # Step 7: Add Column FLOUR Map - Expected Additional SG
# # Payroll_Period_Code['FLOUR Map - expected Additional SG'] = np.where(
# #   Payroll_Period_Code['FLOUR - OTE'] > Payroll_Period_Code['MCB'], 
# #     Payroll_Period_Code['MCB'] * Payroll_Period_Code['Additional Super Rate'],
# #     np.where(
# #       Payroll_Period_Code['FLOUR - OTE'] < Payroll_Period_Code['MCB'],
# #         Payroll_Period_Code['FLOUR - OTE'] * Payroll_Period_Code['Additional Super Rate'],
# #         0
# #     )
# # )

# # row_count = count_rows(Payroll_Period_Code)
# # print(f"The DataFrame has {row_count} rows after Step 7.")






# # row_count = count_rows(Payroll_Period_Code)
# # print(f"The DataFrame has {row_count} rows after Step 8.")


# # grouped_df = Payroll_Period_Code.groupby(
# #     #["Entity", "Emp Code", "Employee Name", "Period_Ending", "MCB", "SG Rate", "Additional Super Rate"], as_index=False
# #     ["Entity", "Emp Code", "Employee Name", "Period_Ending", "MCB"], as_index=False
# # ).agg({
# #     "SW - OTE": "sum",
# #     #lambda x: x.unique()[0] if len(x.unique()) == 1 else 'Check this one my guy',  # Get unique value (or handle duplicates)
# #     "FLOUR - OTE": "sum",
# #     "Payroll Super": "sum",
# #     "SW Map - expected Minimum SG": "sum",
# #     "SW Map expected Additional SG": "sum",
# #     "SW Map - total expected SG": "sum",
# #     "FLOUR Map - expected Minimum SG": "sum",
# #     "FLOUR Map - expected Additional SG": "sum",
# #     "FLOUR Map - Expected Total SG": "sum"
# # })



# # Payroll_Period_Code = grouped_df



# # row_count = count_rows(Payroll_Period_Code)
# # print(f"The DataFrame has {row_count} rows after Step 8b.")

# # # Step 9: Merge Tables
# # # = Table.NestedJoin(#"Inserted Addition1", {"Emp Code", "Period_Ending"}, #"Super Clearing House", {"Employee Id", "FY Quarter"}, "Super Clearing House", JoinKind.LeftOuter)
# # #= Table.ExpandTableColumn(#"Merged Queries1", "Super Clearing House", {"SUPER GUARANTEE (SG)"}, {"Super Clearing House.SUPER GUARANTEE (SG)"})

# # # Perform a left outer join between the two DataFrames
# # # Merge Payroll_Period_Code with super_clearing_house_detail, selecting only the SG column






# # superClearingHouse_summed.to_csv('superClearingHouse_summed_test.csv')




# # unique_payroll_numbers = Payroll_Period_Code['Emp Code'].nunique()

# # print('No. Unique Payroll Values: ')
# # print(unique_payroll_numbers)


# # print('Payroll Vs Super Clear Sum: ')
# # # Identify Payroll Numbers in QTR_Results but not in super_clearing_house_summed
# # payroll_in_qtr_results = Payroll_Period_Code['Emp Code'].unique()
# # payroll_in_super_tpd = superClearingHouse_summed['Employee Id'].unique()

# # # Find mismatched Payroll Numbers
# # mismatched_payroll_numbers = set(payroll_in_qtr_results) - set(payroll_in_super_tpd)
# # print('Payroll Numbers in Payroll Code but NOT in super_clearing_house_summed:')
# # print(mismatched_payroll_numbers)

# # # Optionally, find Payroll Numbers in super_clearing_house_tpd but NOT in QTR_Results
# # extra_payroll_numbers = set(payroll_in_super_tpd) - set(payroll_in_qtr_results)
# # print('Payroll Numbers in Super Clearing House Summed but NOT in Payroll Code:')
# # print(extra_payroll_numbers)






# # QTR_Results = Payroll_Period_Code.merge(
# #     superClearingHouse_summed[['Employee Id', 'FY Quarter', 'SUPER GUARANTEE (SG)']], 
# #     how="left", 
# #     left_on=["Emp Code", "Period_Ending"], 
# #     right_on=["Employee Id", "FY Quarter"]
# # )

# # QTR_Results.to_csv('Step_9_dataframe.csv')

# # print('Step 9 columns: ')
# # print(QTR_Results.columns)


# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 9.")


# # # Step 10: Replace null (NaN) values with 0 in the specified column

# # QTR_Results['SUPER GUARANTEE (SG)'] = QTR_Results['SUPER GUARANTEE (SG)'].fillna(0)

# # 0
# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 10.")


# # # Step 11: Merged queries
# # #= Table.NestedJoin(#"Replaced Value2", {"Emp Code", "Period_Ending"}, 
# # # #"Super Clearing House TPD", {"Payroll Number", "FY Quarter"}, "Super Clearing House TPD", JoinKind.LeftOuter)

# # #= Table.ExpandTableColumn(#"Merged Queries", "Super Clearing House TPD", {"TPD Super"}, {"TPD Super"})

# # #QTR_Results["Emp Code"] = QTR_Results["Emp Code"].astype(int)
# # #super_clearing_house_tpd["Payroll Number"] = super_clearing_house_tpd["Payroll Number"].astype(int)

# # QTR_Results = QTR_Results.drop_duplicates()

# # QTR_Results.to_csv('beforeStep 11MergeCSV.csv')

# # SuperTPDPayNoCount = super_clearing_house_tpd['Payroll Number'].nunique()



# # super_clearing_house_tpd['Payroll Number'] = super_clearing_house_tpd['Payroll Number'] \
# #     .astype(str) \
# #     .str.strip() \
# #     .replace('', float('NaN')) \
# #     .dropna() \
# #     .apply(lambda x: x.zfill(7))  # Adds leading zeros to ensure 5 digits

# # print('SuperTPDPayNoCount: ')
# # print(SuperTPDPayNoCount)

# # placeholder_df = QTR_Results.merge(
# #     super_clearing_house_tpd[['Payroll Number', 'FY Quarter', 'TPD Super']],
# #     how="left",
# #     left_on=["Emp Code", "Period_Ending"],
# #     right_on=["Payroll Number", "FY Quarter"]
# # )

# # print('Step 11: shape')
# # print(QTR_Results.shape)

# # Step11_Test = placeholder_df[['Payroll Number', 'Period_Ending', 'TPD Super']]


# # print('Step 11 - TPD Test')
# # print(Step11_Test.shape)

# # row_count = count_rows(placeholder_df)
# # print(f"The DataFrame has {row_count} rows after Step 11.")

# # # Get unique values for Payroll Number
# # unique_payroll_numbers = Step11_Test['Payroll Number'].nunique()

# # print('No. Unique Payroll Values: ')
# # print(unique_payroll_numbers)

# # # Identify Payroll Numbers in QTR_Results but not in super_clearing_house_tpd
# # payroll_in_qtr_results = QTR_Results['Emp Code'].unique()
# # payroll_in_super_tpd = super_clearing_house_tpd['Payroll Number'].unique()

# # # Find mismatched Payroll Numbers
# # mismatched_payroll_numbers = set(payroll_in_qtr_results) - set(payroll_in_super_tpd)
# # print('Payroll Numbers in QTR_Results but NOT in super_clearing_house_tpd:')
# # print(mismatched_payroll_numbers)

# # # Optionally, find Payroll Numbers in super_clearing_house_tpd but NOT in QTR_Results
# # extra_payroll_numbers = set(payroll_in_super_tpd) - set(payroll_in_qtr_results)
# # print('Payroll Numbers in super_clearing_house_tpd but NOT in QTR_Results:')
# # print(extra_payroll_numbers)









# # # Step 12: Replaced values 
# # # - = Table.ReplaceValue(#"Expanded Super Clearing House TPD",null,0,Replacer.ReplaceValue,{"TPD Super"})
# # # Replace null (NaN) values with 0 in the "TPD Super" column
# # placeholder_df['TPD Super'] = placeholder_df['TPD Super'].fillna(0)



# # QTR_Results = placeholder_df


# # QTR_Results.to_csv('Step_12_Dataframe.csv')




# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 12.")

# # # Step 13: Grouped Rows
# # # = Table.Group(#"Replaced Value", {"Entity", "Emp Code", "Employee Name", "Period_Ending", "MCB"},
# # #  {{"SW - OTE", each List.Sum([#"SW - OTE"]), type number}, {"FLUOR - OTE", each List.Sum([#"FLUOR - OTE"]),
# # #  type number}, {"Payroll Super", each List.Sum([Payroll Super]), type number}, {"SW Map - expected Minimum SG", 
# # # each List.Sum([#"SW Map - expected Minimum SG"]), type number}, {"SW Map - expected Additional SG", 
# # # each List.Sum([#"SW Map - expected Additional SG"]), type number}, {"SW Map - total expected SG", 
# # # each List.Sum([#"SW Map - total expected SG"]), type number}, {"FLUOR Map - Expected Minimum SG",
# # #  each List.Sum([#"FLUOR Map - Expected Minimum SG"]), type number}, {"FLUOR Map - Expected Additional SG",
# # #  each List.Sum([#"FLUOR Map - Expected Additional SG"]), type number}, {"FLUOR Map - Expected Total SG", 
# # # each List.Sum([#"FLUOR Map - Expected Total SG"]), type number}, {"Super Clearing House.SUPER GUARANTEE (SG)",
# # #  each List.Sum([#"Super Clearing House.SUPER GUARANTEE (SG)"]), type nullable number},
# # #  {"TPD Super", each List.Sum([TPD Super]), type nullable number}})



# # # #Group by the specified columns and aggregate others using sum
# # # grouped_df = QTR_Results.groupby(
# # #     #["Entity", "Emp Code", "Employee Name", "Period_Ending", "MCB", "SG Rate", "Additional Super Rate"], as_index=False
# # #     ["Entity", "Emp Code", "Employee Name", "Period_Ending", "MCB"], as_index=False
# # # ).agg({
# # #     "SW - OTE": "sum",
# # #     #lambda x: x.unique()[0] if len(x.unique()) == 1 else 'Check this one my guy',  # Get unique value (or handle duplicates)
# # #     "FLOUR - OTE": "sum",
# # #     "Payroll Super": "sum",
# # #     "SW Map - expected Minimum SG": "sum",
# # #     "SW Map expected Additional SG": "sum",
# # #     "SW Map - total expected SG": "sum",
# # #     "FLOUR Map - expected Minimum SG": "sum",
# # #     "FLOUR Map - expected Additional SG": "sum",
# # #     "FLOUR Map - Expected Total SG": "sum",
# # #     "SUPER GUARANTEE (SG)": "sum",
# # #     "TPD Super": "sum"
# # # })





# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 13.")

# # # Step 14: Inserted Subtraction part 1
# # # = Table.AddColumn(#"Grouped Rows1", "Discrepancy 1 - SW / FLUOR Mapping", 
# # # each Number.Round([#"SW Map - total expected SG"] - [#"FLUOR Map - Expected Total SG"],0), type number)

# # #QTR_Results['Discrepancy 1 - SW / FLUOR Mapping'] = (QTR_Results['SW Map - total expected SG'] - QTR_Results['FLOUR Map - Expected Total SG']).round(0)
# # # Flipped around the formula so that negative numbers are under payments
# # QTR_Results['Discrepancy 1 - SW / FLUOR Mapping'] = (QTR_Results['FLOUR Map - Expected Total SG'] - QTR_Results['SW Map - total expected SG'] ).round(0)


# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 14.")

# # # Step 15: Inserted Subtraction part 2
# # #= Table.AddColumn(#"Inserted Subtraction", "Discrepancy 2 - FLUOR System Calc", each [#"FLUOR Map
# # #  - Expected Total SG"] - [Payroll Super], type number)



# # #QTR_Results['Discrepancy 2 - FLUOR System Calc'] = (QTR_Results['FLOUR Map - Expected Total SG'] - QTR_Results['Payroll Super'])
# # # Flipped around the formula so that negative numbers are under payments
# # QTR_Results['Discrepancy 2 - FLUOR System Calc'] = ( QTR_Results['Payroll Super'] - QTR_Results['FLOUR Map - Expected Total SG'])

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 15.")

# # # Step 16: Inserted Subtraction Part 3
# # #= Table.AddColumn(#"Inserted Subtraction1", "Discrepancy 3 - FLUOR Paid Calc", each [Payroll Super] 
# # # - [#"Super Clearing House.SUPER GUARANTEE (SG)"] - [TPD Super], type number)


# # print(QTR_Results.columns)

# # QTR_Results['Discrepancy 3 - FLUOR Paid Calc'] = (QTR_Results['Payroll Super'] - QTR_Results['SUPER GUARANTEE (SG)'] - QTR_Results['TPD Super'])


# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 16.")


# # # Step 17: Inserted Subtraction Part 4
# # #= Table.AddColumn(#"Inserted Subtraction2", "Discrepancy 4 - SW Expected / SCH Actual", 
# # # each [#"SW Map - total expected SG"] - [#"Super Clearing House.SUPER GUARANTEE (SG)"] 
# # # - [TPD Super], type number)


# # #QTR_Results['Discrepancy 4 - SW Expected / SCH Actual'] = (QTR_Results['SW Map - total expected SG'] - QTR_Results['SUPER GUARANTEE (SG)'] - QTR_Results['TPD Super'])
# # # Flipped around the formula so that negative numbers are under payments
# # QTR_Results['Discrepancy 4 - SW Expected / SCH Actual'] = (QTR_Results['SUPER GUARANTEE (SG)'] - QTR_Results['TPD Super'] - QTR_Results['SW Map - total expected SG'])


# # # Flip around the formula so that negative numbers are under payments

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 17.")


# # # Step 18: Sort rows so in ascending order 

# # QTR_Results = QTR_Results.sort_values(
# #     by=["Emp Code", "Period_Ending"],
# #     ascending=[True, True]  # All columns sorted in ascending order
# # )

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 18.")


# # # 19. Readding the Payroll Super column


# # QTR_Results['SG Rate'] =  np.where(
# #     QTR_Results['Period_Ending'].str.contains('2022', na=False), 
# #     0.1,
# #     np.where(
# #         QTR_Results['Period_Ending'].str.contains('2023', na=False),
# #         0.105,
# #         np.where(
# #             QTR_Results['Period_Ending'].str.contains('2024', na=False),
# #             0.11,
# #             0  # Default value if none of the conditions are met
# #         )
# #     )
# # )



# # # 20. Additional Super column 

# # QTR_Results['Additional Super Rate'] = np.where(
# #   QTR_Results['Entity'] == 'FLUOR',
# #   0.001,
# #   0
# # )




# # # Step 21: Add column for Non-Material Discrepancies 
# # #    [#"Discrepancy 1 - SW / FLUOR Mapping"] >= -0.99 and [#"Discrepancy 1 - SW / FLUOR Mapping"] <= 0.99 and
# # #     [#"Discrepancy 2 - FLUOR System Calc"] >= -0.99 and [#"Discrepancy 2 - FLUOR System Calc"] <= 0.99 and
# # #    [#"Discrepancy 3 - FLUOR Paid Calc"] >= -0.99 and  [#"Discrepancy 3 - FLUOR Paid Calc"] <= 0.99 and
# # #     [#"Discrepancy 4 - SW Expected / SCH Actual"] >= -0.99 and [#"Discrepancy 4 - SW Expected / SCH Actual"] <= 0.99 
# # # then 
# # #     "non-material" 
# # # else 
# # #     "material", type text)



# # # QTR_Results['Non-material discrepancies'] = np.where(
# # #     (QTR_Results['Discrepancy 1 - SW / FLUOR Mapping'] >= -0.99) & 
# # #     (QTR_Results['Discrepancy 1 - SW / FLUOR Mapping'] <= 0.99) &
# # #     (QTR_Results['Discrepancy 2 - FLUOR System Calc'] >= -0.99) &
# # #     (QTR_Results['Discrepancy 2 - FLUOR System Calc'] <= 0.99) &
# # #     (QTR_Results['Discrepancy 3 - FLUOR Paid Calc'] >= -0.99) &
# # #     (QTR_Results['Discrepancy 3 - FLUOR Paid Calc'] <= 0.99) &
# # #     (QTR_Results['Discrepancy 4 - SW Expected / SCH Actual'] >= -0.99) &
# # #    (QTR_Results['Discrepancy 4 - SW Expected / SCH Actual'] <= 0.99),
# # #     'non-material',
# # #     'material'
    
# # # )

# # #Add a new column for Non-Material Discrepancies
# # QTR_Results['Non-material discrepancies'] = np.where(
# #     (QTR_Results['Discrepancy 1 - SW / FLUOR Mapping'].between(-0.99, 0.99)) &
# #     (QTR_Results['Discrepancy 2 - FLUOR System Calc'].between(-0.99, 0.99)) &
# #     (QTR_Results['Discrepancy 3 - FLUOR Paid Calc'].between(-0.99, 0.99)) &
# #     (QTR_Results['Discrepancy 4 - SW Expected / SCH Actual'].between(-0.99, 0.99)),
# #     "non-material",
# #     "material"
# # )

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 21.")





# # def count_non_material(df, column_name):
# #     """
# #     Counts the number of 'non-material' values in the specified column of a DataFrame.

# #     Args:
# #         df (pd.DataFrame): The DataFrame to analyze.
# #         column_name (str): The name of the column to search for 'non-material' values.

# #     Returns:
# #         int: The count of 'non-material' values.
# #     """
# #     return df[column_name].value_counts().get("non-material", 0)

# # # Example usage:
# # non_material_count = count_non_material(QTR_Results, 'Non-material discrepancies')
# # print(f"Number of non-material discrepancies: {non_material_count}")



# # print('QTR Results columns: ')
# # print(QTR_Results.columns)


# # # Step 22: adding Discrepency 1 comment column

# # # Adding the new column 
# # QTR_Results["SW Comment - Discrepancy 1"] = np.where(
# #     QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] == 0, "No discrepancy",
# #     np.where(
# #         QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] == QTR_Results["SW Map expected Additional SG"], "Missing additional super (0.5%)",
# #         np.where(
# #             QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] >= 1, "Under - mapping config issue",
# #             np.where(
# #                 QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] <= -1, "Over - mapping config difference",
# #                 np.where(
# #                     (-1 < QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"]) & (QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] < 1), "No discrepancy",
# #                     None
# #                 )
# #             )
# #         )
# #     )
# # )


# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 22.")


# # # Step 23: Adding Discrepency 2 comment column

# # QTR_Results["SW Comment - Discrepancy 2"] = np.where(
# #     (QTR_Results["Discrepancy 2 - FLUOR System Calc"] < 1) & 
# #     (QTR_Results["Discrepancy 2 - FLUOR System Calc"] > -1), "No discrepancy",
# #     np.where(
# #         (QTR_Results["Discrepancy 2 - FLUOR System Calc"] != 0) & 
# #         ((QTR_Results["FLOUR - OTE"] * 
# #           (QTR_Results["SG Rate"] + QTR_Results["Additional Super Rate"]) - 
# #           QTR_Results["Payroll Super"]) < 1) & 
# #         ((QTR_Results["FLOUR - OTE"] * 
# #           (QTR_Results["SG Rate"] + QTR_Results["Additional Super Rate"]) - 
# #           QTR_Results["Payroll Super"]) > -1), "Not capping",
# #         np.where(
# #             QTR_Results["FLOUR Map - Expected Total SG"] == 
# #             QTR_Results["Discrepancy 2 - FLUOR System Calc"], "No payroll super",
# #             np.where(
# #                 QTR_Results["Discrepancy 2 - FLUOR System Calc"] >= 1, "Under - System calc issue",
# #                 np.where(
# #                     QTR_Results["Discrepancy 2 - FLUOR System Calc"] <= -1, "Over - System calc difference",
# #                     None
# #                 )
# #             )
# #         )
# #     )
# # )

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 23.")


# # # Step 24: Adding Discrepency 3 comment column

# # QTR_Results["SW Comment - Discrepancy 3"] = np.where(
# #     QTR_Results["Discrepancy 3 - FLUOR Paid Calc"] >= 1, "Under - Actual paid issue",
# #     np.where(
# #         QTR_Results["Discrepancy 3 - FLUOR Paid Calc"] <= -1, "Over - Actual paid difference",
# #         np.where(
# #             QTR_Results["Discrepancy 3 - FLUOR Paid Calc"] < -1, "No discrepancy",
# #             np.where(
# #                 QTR_Results["Discrepancy 3 - FLUOR Paid Calc"] > -1, "No discrepancy",
# #                 None
# #             )
# #         )
# #     )
# # )

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 24.")


# # # Step 25: Adding Discrepency 4 comment column

# # QTR_Results["SW Comment - Discrepancy 4"] = np.where(
# #     (QTR_Results["SW Comment - Discrepancy 1"] == "No discrepancy") & 
# #     (QTR_Results["SW Comment - Discrepancy 3"] == "No discrepancy") & 
# #     (QTR_Results["SW Comment - Discrepancy 2"] == "No super"), "No Super",
# #     np.where(
# #         QTR_Results["Discrepancy 1 - SW / FLUOR Mapping"] == 
# #         QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"], QTR_Results["SW Comment - Discrepancy 1"],
# #         np.where(
# #             (QTR_Results["SW Comment - Discrepancy 1"] == "No discrepancy") & 
# #             (QTR_Results["Discrepancy 2 - FLUOR System Calc"] == QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"]),
# #             QTR_Results["SW Comment - Discrepancy 2"],
# #             np.where(
# #                 (QTR_Results["SW Comment - Discrepancy 1"] != "No discrepancy") & 
# #                 (QTR_Results["SW Comment - Discrepancy 2"] != "No discrepancy") & 
# #                 (QTR_Results["SW Comment - Discrepancy 3"] == "No discrepancy"),
# #                 QTR_Results["SW Comment - Discrepancy 1"] + " & " + QTR_Results["SW Comment - Discrepancy 2"],
# #                 np.where(
# #                     (QTR_Results["SW Comment - Discrepancy 1"] != "No discrepancy") & 
# #                     (QTR_Results["SW Comment - Discrepancy 2"] == "No discrepancy") & 
# #                     (QTR_Results["SW Comment - Discrepancy 3"] == "No discrepancy"),
# #                     QTR_Results["SW Comment - Discrepancy 1"],
# #                     np.where(
# #                         (QTR_Results["SW Comment - Discrepancy 1"] == "No discrepancy") & 
# #                         (QTR_Results["SW Comment - Discrepancy 2"] == "No discrepancy") & 
# #                         (QTR_Results["SW Comment - Discrepancy 3"] != "No discrepancy"),
# #                         QTR_Results["SW Comment - Discrepancy 3"],
# #                         np.where(
# #                             (QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"] >= 1), "Under",
# #                             np.where(
# #                                 (QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"] <= -1), "Over",
# #                                 np.where(
# #                                     (-1 < QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"]) & 
# #                                     (QTR_Results["Discrepancy 4 - SW Expected / SCH Actual"] < 1), "No discrepancy",
# #                                     None
# #                                 )
# #                             )
# #                         )
# #                     )
# #                 )
# #             )
# #         )
# #     )
# # )

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 25.")








# # # Step 26: Rename columns
# # QTR_Results = QTR_Results.rename(columns={
# #     "Emp Code": "Employee Code",  # Rename "Emp Code" to "Employee Code"
# #     "MCB": "Maximum Contribution Base",  # Rename "MCB" to "Maximum Contribution Base"
# #     "SW Map - expected Minimum SG": "SW Map - Expected Minimum SG",  # Correct capitalization
# #     "SW Map - expected Additional SG": "SW Map - Expected Additional SG",  # Correct capitalization
# #     "SW Map - total expected SG": "SW Map - TOTAL Expected SG",  # Adjust capitalization
# #     "FLUOR Map - Expected Total SG": "FLUOR Map - TOTAL Expected SG",  # Adjust capitalization
# #     "Payroll Super": "Payroll - Total SG Paid",  # Rename "Payroll Super" to "Payroll - Total SG Paid"
# #     "SUPER GUARANTEE (SG)": "SCH - Total SG Received",  # Shorten and clarify
# #     "Discrepancy 1 - SW / FLUOR Mapping": "Discrepancy 1 - SW / FLUOR Mapped Expected SG",  # Provide detailed context
# #     "Discrepancy 2 - FLUOR System Calc": "Discrepancy 2 - FLUOR Map Expected / Payroll Paid",  # Provide detailed context
# #     "Discrepancy 3 - FLUOR Paid Calc": "Discrepancy 3 - Payroll Paid / SCH Received",  # Provide detailed context
# #     "Discrepancy 4 - SW Expected / SCH Actual": "Discrepancy 4 - SW Expected / SCH Received"  # Provide detailed context
# # })

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 26.")
# # # Step 27: Reorder columns
# # QTR_Results = QTR_Results[
# #     [
# #         "Entity",  # Entity column
# #         "Employee Code",  # Employee Code column
# #         "Employee Name",  # Employee Name column
# #         "Period_Ending",  # Period_Ending column
# #         "SW - OTE",  # SW - OTE column
# #         "FLOUR - OTE",  # FLUOR - OTE column
# #         "Maximum Contribution Base",  # Maximum Contribution Base column
# #         'TPD Super',
# #         "SW Map - Expected Minimum SG",  # SW Map - Expected Minimum SG column
# #         "SW Map expected Additional SG",  # SW Map - Expected Additional SG column
# #         "FLOUR Map - expected Minimum SG",  # FLUOR Map - Expected Minimum SG column
# #         "FLOUR Map - expected Additional SG",  # FLUOR Map - Expected Additional SG column
# #         "SW Map - TOTAL Expected SG",  # SW Map - TOTAL Expected SG column
# #         "FLOUR Map - Expected Total SG",  # FLUOR Map - TOTAL Expected SG column
# #         "Payroll - Total SG Paid",  # Payroll - Total SG Paid column
# #         "SCH - Total SG Received",  # SCH - Total SG Received column
# #         "Discrepancy 1 - SW / FLUOR Mapped Expected SG",  # Discrepancy 1 column
# #         "Discrepancy 2 - FLUOR Map Expected / Payroll Paid",  # Discrepancy 2 column
# #         "Discrepancy 3 - Payroll Paid / SCH Received",  # Discrepancy 3 column
# #         "Discrepancy 4 - SW Expected / SCH Received",  # Discrepancy 4 column
# #         "Non-material discrepancies",  # Non-material discrepancies column
# #         "SW Comment - Discrepancy 1",  # SW Comment - Discrepancy 1 column
# #         "SW Comment - Discrepancy 2",  # SW Comment - Discrepancy 2 column
# #         "SW Comment - Discrepancy 3",  # SW Comment - Discrepancy 3 column
# #         "SW Comment - Discrepancy 4"  # SW Comment - Discrepancy 4 column
# #     ]
# # ]

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 27.")

# # # Step 28: add new column called Qtr Key
# # QTR_Results['Employee Code'] = QTR_Results['Employee Code'].astype(str)


# # # Add a new column "Qtr Key" by concatenating "Employee Code" and "Period_Ending"
# # QTR_Results["Qtr Key"] = QTR_Results["Employee Code"] + QTR_Results["Period_Ending"]

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 28.")

# # # Step 29: add new column FY

# # QTR_Results['FY'] = np.where(
# #     QTR_Results['Period_Ending'].str.contains('2022', na=False), '2022',
# #     np.where(
# #         QTR_Results['Period_Ending'].str.contains('2023', na=False), '2023',
# #         np.where(
# #             QTR_Results['Period_Ending'].str.contains('2024', na=False), '2024',
# #             '0'
# #         )
# #     )
# # )

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 29.")

# # # Step 30: Change FY column data type 
# # QTR_Results['FY'] = QTR_Results['FY'].astype(str)

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 30.")

# # # Step 31: Add a new column called FY Key
# # QTR_Results['FY Key'] = QTR_Results['Employee Code'] + QTR_Results['FY']

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 31.")


# # # Step 32: Change FY Key data type 
# # QTR_Results['FY Key'] = QTR_Results['FY Key'].astype(str)

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 32.")


# # # Step 32.b: Unfiltered QTR Results
# # QTR_Results.to_csv('QTR Results unfiltered.csv')


# # # Step 33: Filter dataframe to only includes rows where Non-material discrepancies column is equal to 'material' 
# # QTR_Results =  QTR_Results[QTR_Results['Non-material discrepancies'] == 'material']

# # row_count = count_rows(QTR_Results)
# # print(f"The DataFrame has {row_count} rows after Step 33.")


# # # Displaying the DataFrame with the new column
# # print(QTR_Results)


# # QTR_Results.to_csv('QTR_ResultsTest.csv') 


# # # Annual Results

# # # Step 1: Establish source
# # Annual_Results = QTR_Results

# # # Step 2: Add Column - Annual MCB

# # Annual_Results['Annual MCB'] = np.where(
# #     Annual_Results['FY'].str.contains('2022', na=False), 235680,
# #     np.where(
# #         Annual_Results['FY'].str.contains('2023', na=False), 240880,
# #         np.where(
# #             Annual_Results['FY'].str.contains('2024'), 186810,
# #             0
# #         )
# #     )
# # )

# # # Step 3: Change data type of Annual MCB column

# # Annual_Results['Annual MCB'] = Annual_Results['Annual MCB'].astype('Int64')


# # # Step 4: Add column for super rate

# # Annual_Results['Super Rate'] = np.where(
# #     Annual_Results['FY'].str.contains('2022', na=False), 0.1,
# #     np.where(
# #         Annual_Results['FY'].str.contains('2023', na=False), 0.105,
# #         np.where(
# #             Annual_Results['FY'].str.contains('2024', na=False), 0.11,
# #             0
# #         )
# #     )
# # )


# # # Step 5: insert column Super up to  MCB


# # Annual_Results['Super up to MCB'] = Annual_Results['Super Rate'] * Annual_Results['Annual MCB']


# # print('Annual_Results columns: ')
# # print(Annual_Results.columns)

# # # Step 6: Group the data frame

# # Annual_Results = Annual_Results.groupby(
# #     ["Entity", "Employee Code", "Employee Name", "FY", "Annual MCB", "Super Rate", "Super up to MCB", "FY Key"]
# # ).agg({
# #     "SW - OTE": "sum",
# #     "FLOUR - OTE": "sum",
# #     "SW Map - TOTAL Expected SG": "sum",
# #     "FLOUR Map - Expected Total SG": "sum",
# #     "Payroll - Total SG Paid": "sum",
# #     "SCH - Total SG Received": "sum",  # If nullable, pandas handles missing values in summation
# #     "TPD Super": "sum"                 # Similarly, handles nullable values
# # }).reset_index()


# # # Step 7: Add column total super received

# # Annual_Results['TOTAL SUPER RECEIVED'] = Annual_Results['SCH - Total SG Received'] + Annual_Results['TPD Super']

# # # # Step 8: Add column Check Cap

# # # Annual_Results['Check Cap'] = np.where(
# # #     Annual_Results['TOTAL SUPER RECEIVED'] >= Annual_Results['Super up to MCB'],
# # #     'Above / met cap',
# # #     np.where(
# # #         Annual_Results['TOTAL SUPER RECEIVED'] < Annual_Results['Super up to MCB'],
# # #         'Below Cap',
# # #         0
# # #     )
# # # )

# # # # Step 9: Change data type of Check Cap column

# # # Annual_Results['Check Cap'] = Annual_Results['Check Cap'].astype(str)

# # # Annual_Results.to_csv('Annual_Results.csv')