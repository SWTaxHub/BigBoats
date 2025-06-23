import pandas as pd
import numpy as np

#Declare Flour file path
Payroll_filepath = r"C:\Git\BigBoats\FLour\Effected.Emp_Shortfall_S&W_Payroll.Detail.xlsx"


Payroll_data = pd.read_excel(Payroll_filepath, sheet_name='Payroll_Period_S_W__2')



# Rename columns for consistency
column_mapping = {
        'Employee Code' : 'Emp_Code',
        'Employee Name' : 'Employee_Name',
        'PE Date' : 'Period_Ending_Date',
        'Pay Period Quarter' : 'Pay_Period_Quarter',
        'Qtr Key' : 'Qtr_Key',
        'SG rate' : 'SG_Rate',
        'Additional Super Rate' : 'Additional_Super_Rate',
        'Pay Attribute Code' : 'Pay_Attribute_Code',
        'Pay Attribute Description' : 'Pay_Attribute_Description',
        'Client Mapping' : 'Client_Mapping',
        'SW mapping' : 'SW_mapping',
        'Client Map - OTE' : 'Client_Mapping_OTE',
        'Client Map - SG on OTE' : 'Client_Mapping_SG_on_OTE',
        'Client Map - Additional SG on OTE' : 'Client_Mapping_Additional_SG_on_OTE',
        'SW Map - OTE' : 'SW_Mapping_OTE',
        'SW Map - SG on OTE' : 'SW_Mapping_SG_on_OTE',
        'SW Map - SG on S&W' : 'SW_Mapping_SG_on_S_W',
        'SW Map - Total S&W SG' : 'SW_Mapping_Total_S_W_SG',
        'Client Payroll - Super Paid' : 'Payroll_actual_SG_paid'
    }
Payroll_data.rename(columns=column_mapping, inplace=True)

    # Convert Data Types
Payroll_data['Emp_Code'] = Payroll_data['Emp_Code'].astype(str)
Payroll_data['Pay_Period_Quarter'] = Payroll_data['Pay_Period_Quarter'].astype(str)
Payroll_data['Qtr_Key'] = Payroll_data['Qtr_Key'].astype(str)
Payroll_data['SG_Rate'] = Payroll_data['SG_Rate'].astype(float)
Payroll_data['Hrs'] =  Payroll_data['Hrs'].astype(float)
Payroll_data['Amt'] = Payroll_data['Amt'].astype(float)
Payroll_data['Client_Mapping_OTE'] = Payroll_data['Client_Mapping_OTE'].astype(float)
Payroll_data['SW_Mapping_OTE'] = Payroll_data['SW_Mapping_OTE'].astype(float)
Payroll_data['Additional_Super_Rate'] = Payroll_data['Additional_Super_Rate'].astype(float)

Payroll_data['Payroll_actual_SG_paid'] = Payroll_data['Payroll_actual_SG_paid'].astype(float)





def calculate_shortfall_offset(Payroll_data):
    agg_methods = {
        'Employee_Name' : 'first',  
        'Qtr_Key' : 'first',
       'Pay_Period_Quarter' : 'first',
        'Hrs': 'sum',
        'Amt': 'sum',
        'SG_Rate': 'mean',
        'Pay_Period_Quarter': 'first',
        'Client_Mapping_OTE' : 'sum',
        'Client_Mapping_SG_on_OTE' : 'sum',
        'Client_Mapping_Additional_SG_on_OTE' : 'sum',
        'SW_Mapping_OTE' : 'sum',
        'SW_Mapping_SG_on_OTE' : 'sum',
        'SW_Mapping_SG_on_S_W' : 'sum',
        'SW_Mapping_Total_S_W_SG' : 'sum',
        'Payroll_actual_SG_paid' : 'sum',
    }

# Commented out as PIN is not equivalent to Pay_Number
   # df1 = mergedData_Labour.groupby(['Period_Ending_Date', 'Pin', 'Emp_Code']).agg(agg_methods).reset_index()

    df1 = Payroll_data.groupby(['Period_Ending_Date', 'Emp_Code']).agg(agg_methods).reset_index()
    df1 = df1.sort_values(by=['Emp_Code', 'Period_Ending_Date'])



    df1['SW_Mapping_SG_on_OTE'] = df1['SW_Mapping_SG_on_OTE'].round(2)
    df1['Shortfall SG'] = df1['Payroll_actual_SG_paid'] - df1['SW_Mapping_SG_on_OTE']
    df1['Shortfall SG_cumulative_sum'] = df1.groupby(['Emp_Code'])['Shortfall SG'].cumsum()

    df1 = df1.sort_values(by=['Emp_Code', 'Period_Ending_Date'])

    df1['cumulative_sum_12Months_OVERPAY'] = df1.groupby('Emp_Code').apply( # Grouped the DataFrame by 'Emp_Code' to process each employee separately
        lambda g: g.apply(
            # apply() will operate on each group (i.e. all rows for one employee).
            # For each group g (i.e. one employee’s data), applying another function row by row.
            lambda row: g.loc[
                # For each row, locate all other rows within the same group (employee) that meet the following conditions:
                #The Period_Ending_Date is within the past 12 months from the current row’s date (exclusive of the lower bound, inclusive of the upper bound).
                # The Shortfall SG is greater than 0.01 (i.e., it is considered an overpayment).
                (g['Period_Ending_Date'] > row['Period_Ending_Date'] - pd.DateOffset(years=1)) &
                (g['Period_Ending_Date'] <= row['Period_Ending_Date']) &
                (g['Shortfall SG'] > 0.01),
                #From the filtered rows, extract the 'Shortfall SG' column and sum it.
                # This sum becomes the cumulative 12-month overpayment for that row.
                'Shortfall SG'
            ].sum(), axis=1)
    ).reset_index(level=0, drop=True)

    # Flags whether a negative shortfall should be adjusted based on prior overpayments.
    # If: 'Shortfall SG' is negative (indicating an underpayment refund or reversal),
    # AND there was some overpayment in the prior 12 months (cumulative_sum_12Months_OVERPAY > 0),
    # Then: assign 'Y' (Yes, adjust the shortfall),
    # Else: assign 'N' (No adjustment needed).

    df1['Adjust_shortfall_Y/N'] = np.where(
        (df1['Shortfall SG'] < 0) & (df1['cumulative_sum_12Months_OVERPAY'] > 0), 'Y', 'N'
    )

    # This creates a rolling total of "adjustable" shortfalls over the past 12 months, per employee, 
    # helping you track how much of a negative balance can reasonably be corrected based on historical overpayments.

    # Look back 12 months, Add up all the shortfalls that are marked as 'Y' in Adjust_shortfall_Y/N i.e. that can be offset.
    # This is done for each employee separately.
    # "Save that total as a rolling 'adjustment balance' that can be used going forward."

   # df1['cumulative_sum_12Months'] 
    df1['rolling_12M_adjustable_shortfall'] = df1.groupby('Emp_Code').apply(
        lambda g: g.apply(
            lambda row: g.loc[
                (g['Period_Ending_Date'] > row['Period_Ending_Date'] - pd.DateOffset(years=1)) &
                (g['Period_Ending_Date'] <= row['Period_Ending_Date']) &
                (g['Adjust_shortfall_Y/N'] == 'Y'),
                'Shortfall SG'
            ].sum(), axis=1)
    ).reset_index(level=0, drop=True)



   # This column represents how much "room" or "budget" is available to apply shortfall adjustments 
# for the employee at a given point in time. It combines:
# - Overpayments in the past 12 months (cumulative_sum_12Months_OVERPAY), and
# - Previously tracked adjustable shortfalls (rolling_12M_adjustable_shortfall).
# 
# In effect:
# "If this shortfall is eligible for adjustment, how much total balance (overpayment + prior eligible reversals)
# do we have available to offset it?"

    df1['Remaining_Adjustment_Balance'] = np.where(
        df1['Adjust_shortfall_Y/N'] == 'Y', 
        df1['cumulative_sum_12Months_OVERPAY'] + df1['rolling_12M_adjustable_shortfall'],
        np.nan
    )

    # This column flags how a negative shortfall should be treated:
# - 'Y' (Yes): Fully offset — the Remaining_Adjustment_Balance is greater than the absolute shortfall.
# - 'P' (Partial): Some overpayment exists, but it's less than the full shortfall.
# - 'N' (No): No adjustment — either the shortfall isn't negative, or there's no overpayment available to offset it.


    df1['Offset_Shortfall_Y/N'] = np.where(
        (df1['Shortfall SG'] < 0) & (df1['Remaining_Adjustment_Balance'] > abs(df1['Shortfall SG'])), 'Y',
        np.where(
            (df1['Shortfall SG'] < 0) & (df1['cumulative_sum_12Months_OVERPAY'] > 0) & 
            (abs(df1['Remaining_Adjustment_Balance']) < abs(df1['Shortfall SG'])), 'P',
            'N'
        )
    )

    # Calculates how much of the shortfall can be reduced (offset) based on eligibility:
# - If 'Y' (fully offsettable): use the full shortfall amount.
# - If 'P' (partially offsettable): reduce only by the available balance (not the full shortfall).
# - If 'N' (not offsettable): no reduction applied (set to 0).

    df1['Shortfall_Reduction'] = np.where(
        df1['Offset_Shortfall_Y/N'] == 'Y',
        df1['Shortfall SG'],
        np.where(df1['Offset_Shortfall_Y/N'] == 'P', 
                 -(abs(df1['Shortfall SG']) - abs(df1['Remaining_Adjustment_Balance'])),
                 np.where(df1['Offset_Shortfall_Y/N'] == 'N', 0, 0))
    )


    # Calculates the portion of the shortfall that remains unpaid after applying any available offsets:
# - If offset is not allowed and there’s no adjustment balance: keep the full shortfall.
# - If offset is partial but no adjustment balance is left: show the remaining (negative) balance.
# - If offset is not allowed but shortfall is still negative: keep it as-is.
# - Otherwise (fully offset or not relevant): set to 0.

    df1['Remaining_Shortfall_Balance'] = np.where(
        ((df1['Remaining_Adjustment_Balance'] <= 0) & (df1['Offset_Shortfall_Y/N'] == 'N')), df1['Shortfall SG'],
        np.where(
            ((df1['Remaining_Adjustment_Balance'] <= 0) & (df1['Offset_Shortfall_Y/N'] == 'P')), df1['Remaining_Adjustment_Balance'],
            np.where(
                ((df1['Offset_Shortfall_Y/N'] == 'N') & (df1['Shortfall SG'] < 0)), df1['Shortfall SG'],
                0
            )
        )
    )

    # Calculates the date exactly one year before each row's 'Period_Ending_Date'.
# Used for lookback logic in rolling 12-month calculations.

    df1['One_Year_Prior'] = df1['Period_Ending_Date'] - pd.DateOffset(years=1)



# Future looking offset cakculation
    df1['Future_Offset'] = df1.groupby('Emp_Code').apply(
        lambda g: g.apply(
            lambda row: g.loc[
                (g['Period_Ending_Date'] > row['Period_Ending_Date']) &
                (g['Shortfall SG'] < 0) &
                (g['Adjust_shortfall_Y/N'] == 'Y'),
                'Shortfall SG'
            ].sum(), axis=1)
    ).reset_index(level=0, drop=True)





    
  

 # df1['cumulative_sum_12Months'] 
    df1['rolling_12M_adjustable_shortfall'] = df1.groupby('Emp_Code').apply(
        lambda g: g.apply(
            lambda row: g.loc[
                (g['Period_Ending_Date'] > row['Period_Ending_Date'] - pd.DateOffset(years=1)) &
                (g['Period_Ending_Date'] <= row['Period_Ending_Date']) &
                (g['Adjust_shortfall_Y/N'] == 'Y'),
                'Shortfall SG'
            ].sum(), axis=1)
    ).reset_index(level=0, drop=True)



    return df1




employee_list = [ 
# '81318',
# '81319',
# '12711',
# '15290',
# '15241',
# '81316',
# '14503',
# '15413',
# '81127',
# '15173',
# '13297',
# '81401',
# '15332',
# '15423',
# '15224',
# '81165',
#
'13427',
'15119',
'15167',
'15267',
'15274',
'15302',
'15309',
'15337',
'35060'

]





QTR_payroll = pd.read_excel(r"C:\Git\BigBoats\FLour\Payroll data_190625.xlsx", sheet_name='Employee Pay Period')

QTR_payroll['Emp Code'] = QTR_payroll['Emp Code'].astype(str)


condensed_data = QTR_payroll[QTR_payroll['Emp Code'].isin(employee_list)]




condensed_data.to_csv('Condensed_Payroll_Data.csv', index=False)

offset = calculate_shortfall_offset(Payroll_data)

# offset_condensed = calculate_shortfall_offset(condensed_data)
# Save the results to a CSV file
offset.to_csv('RollingShortfallOffset_output_Flour.csv', index=False)

# offset_condensed.to_csv('RollingShortfallOffset_output_Flour_Condensed.csv', index=False)