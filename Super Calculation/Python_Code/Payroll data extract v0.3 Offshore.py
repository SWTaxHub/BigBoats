# Txt to CSV for Payroll reports

import re
import pandas as pd
import numpy as np
from datetime import date
import decimal

# Set rounding mode to ROUND_HALF_UP
decimal.getcontext().rounding = decimal.ROUND_HALF_UP

# ------------------------------------------------------------------------------------
# File paths (choose one)
# ------------------------------------------------------------------------------------
# FY23 OFFSHORE (example)
#Text_part1 = r"C:\Users\smits\Downloads\Pay_Details_History_Offshore_22_23 (2).txt"

# Other examples (comment/uncomment as needed)
#Text_part1 = r"C:\Users\smits\Downloads\Pay_Details_History_Offshore_23_24.txt"
# Text_part1 = r"C:\Users\smits\Downloads\Pay_Details_History_Offshore_24_25.txt"
Text_part1 = r"C:\Users\smits\Downloads\Pay_Details_History_OFFSHORE_FY25_INCLADJ.txt"
# Text_part1 = r"C:\Users\smits\Downloads\Pay_Details_History_Labour22_23_Part1.txt"
# Text_part1 = r"C:\Users\smits\Downloads\Pay_Details_History_Labour22-23_Part1_Excl_ADJ.txt"

# ------------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------------
def safe_round(x):
    """Round to 2 decimals using Decimal(ROUND_HALF_UP) and handle non-numeric safely."""
    try:
        return float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.01')))
    except (decimal.InvalidOperation, ValueError, TypeError):
        return np.nan

# ------------------------------------------------------------------------------------
# Core parser
# ------------------------------------------------------------------------------------
def process_payroll_file(filepath):
    """
    Parse an Attache Payroll Pay Details History text file and return a DataFrame
    containing line-level entries with header fields carried across each block.

    Fixes:
      - Proper extraction of Code_ (location code) and Pay No.
      - Supports 4–5 digit pay numbers.
      - Avoids overwriting regex objects with values.
      - Keeps your downstream calculation logic intact.
    """

    # Read the file
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()

    records = []

    # Block-level context
    period_ending = ""
    full_name = ""
    code_ = ""          # e.g. CANP, YOUC, CORG, JONC, ZISG
    pay_no_value = ""   # e.g. 9997, 10007, etc.
    pay_freq = ""       # Monthly / Weekly / Fortnightly
    is_termination = False

    # Regex patterns
    # If you need the old pattern for ad-hoc checks:
    payno_regex = re.compile(r"\b\w+\s+\w+\s+(\d{4,5})\s+Monthly\b", re.IGNORECASE)

    period_pattern = re.compile(r"Period Ending:\s+(\d{2}/\d{2}/\d{2})")

    # Header pattern: capture 4-digit or 5-digit pay numbers + pay freq variants
    header_pattern = re.compile(
        r"^\s*(?P<loc>\w{4})\s+(?P<pay_point>\w+)\s+(?P<pay_no>\d{4,5})\s+(?P<pay_freq>Monthly|Weekly|Fortnightly)\b",
        flags=re.IGNORECASE | re.MULTILINE
    )

    # Names like "PHILIP CANDLER                             BANK"
    name_pattern = re.compile(r"([A-Z][A-Z\s'\-]+)\s+BANK")

    # Line patterns
    # Leading letter group: N,E,T,B,O,A,C,D lines
    line_pattern = re.compile(
        r"^\s*([NETBOACD])\s+(\S+)\s+(.+?)\s+(-?[\d\.]+)\s+(-?[\d\.]+)(?:/H)?(?:/W)?(?:\s+(-?[\d\.]+))?",
        flags=re.MULTILINE
    )

    # Super lines (E 9, E 8, E SUPER)
    super_line_pattern = re.compile(
        r"^\s*E\s+(9|8|SUPER)\s+(.+?)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)",
        flags=re.MULTILINE
    )

    # Tax lines start with T
    tax_line_pattern = re.compile(
        r"^\s*T\s+(\S+)\s+(.+?)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)",
        flags=re.MULTILINE
    )

    # HRSBNS lines
    hrsbn_pattern = re.compile(
        r"^\s*(N|O|W)\s+HRSBNS\s+(.+?)\s+(\d+\.\d+)\s+(\d+\.\d+)\s*/H\s+(\d+\.\d+)"
    )

    # Loop through lines
    for raw_line in lines:
        # Optional: normalize any HTML entities if present
        line = raw_line.replace("&amp;", "&").replace("&gt;", ">")

        # Detect Period Ending header; start a new block
        m_period = period_pattern.search(line)
        if m_period:
            period_ending = m_period.group(1)
            is_termination = False
            # Reset block header fields so they don't leak across blocks
            code_ = ""
            pay_no_value = ""
            pay_freq = ""
            full_name = ""

            # Insert a marker row (optional, can be removed)
            records.append({
                "Period Ending": period_ending,
                "Code_": "",
                "Full Name": "",
                "Pay No.": "",
                "Line": "",
                "Code": "",
                "Description": "",
                "Hours/Value": "",
                "Pay Rate": "",
                "Addition": "",
                "Deduction": "",
                "Contrib": "",
                "Total": "",
                "Cost Centre": "",
                "Emp Group": "",
                "Is Termination": ""
            })
            continue

        # Extract block's header fields: loc code, pay_no, pay_freq
        m_header = header_pattern.search(line)
        if m_header:
            code_ = m_header.group('loc')
            pay_no_value = m_header.group('pay_no')
            pay_freq = m_header.group('pay_freq').title()
            continue

        # Detect termination indicators
        if any(term_key in line for term_key in [
            "Termination Pay A:", "Termination Pay B:", "Termination Pay D:",
            "ETP Taxable:", "ETP Tax-free:"
        ]):
            is_termination = True
            continue

        # Full name line
        m_name = name_pattern.search(line)
        if m_name:
            full_name = m_name.group(1).strip()
            continue

        # Super lines
        m_super = super_line_pattern.search(line)
        if m_super:
            code, desc, hours, rate, contrib = m_super.groups()
            records.append({
                "Period Ending": period_ending,
                "Code_": code_,
                "Full Name": full_name,
                "Pay No.": pay_no_value,
                "Line": "E",
                "Code": code,
                "Description": desc.strip(),
                "Hours/Value": hours,
                "Pay Rate": rate,
                "Addition": "",
                "Deduction": "",
                "Contrib": contrib,
                "Total": "",
                "Cost Centre": "-NO COSTING-",
                "Emp Group": "",
                "Is Termination": is_termination
            })
            continue

        # Tax lines
        m_tax = tax_line_pattern.search(line)
        if m_tax:
            code, desc, hours, rate, deduction = m_tax.groups()
            records.append({
                "Period Ending": period_ending,
                "Code_": code_,
                "Full Name": full_name,
                "Pay No.": pay_no_value,
                "Line": "T",
                "Code": code,
                "Description": desc.strip(),
                "Hours/Value": hours,
                "Pay Rate": rate,
                "Addition": "",
                "Deduction": deduction,
                "Contrib": "",
                "Total": "",
                "Cost Centre": "-NO COSTING-",
                "Emp Group": "",
                "Is Termination": is_termination
            })
            continue

        # Generic lines (N, O, A, C, D, B, E covered by pattern’s group)
        m_line = line_pattern.search(line)
        if m_line:
            line_code, code, desc, hours, rate, addition = m_line.groups()
            records.append({
                "Period Ending": period_ending,
                "Code_": code_,
                "Full Name": full_name,
                "Pay No.": pay_no_value,
                "Line": line_code,
                "Code": code,
                "Description": desc.strip(),
                "Hours/Value": hours,
                "Pay Rate": rate,
                "Addition": addition if addition is not None else "",
                "Deduction": "",
                "Contrib": "",
                "Total": "",
                "Cost Centre": "-NO COSTING-",
                "Emp Group": "",
                "Is Termination": is_termination
            })
            continue

        # HRSBNS lines (if present)
        m_hrsbn = hrsbn_pattern.match(line)
        if m_hrsbn:
            line_code, desc, hours, rate, addition = m_hrsbn.groups()
            records.append({
                "Period Ending": period_ending,
                "Code_": code_,
                "Full Name": full_name,
                "Pay No.": pay_no_value,
                "Line": line_code,
                "Code": "HRSBNS",
                "Description": desc.strip(),
                "Hours/Value": hours,
                "Pay Rate": rate,
                "Addition": addition,
                "Deduction": "",
                "Contrib": "",
                "Total": "",
                "Cost Centre": "-NO COSTING-",
                "Emp Group": "",
                "Is Termination": is_termination
            })
            continue

    # Convert to DataFrame
    df = pd.DataFrame(records, columns=[
        "Period Ending", "Code_", "Full Name", "Pay No.", "Line", "Code",
        "Description", "Hours/Value", "Pay Rate", "Addition", "Deduction",
        "Contrib", "Total", "Cost Centre", "Emp Group", "Is Termination"
    ])

    # Data cleaning and type conversion
    df["Pay Rate"] = pd.to_numeric(df["Pay Rate"].replace("", "0"), errors="coerce").fillna(0.0)
    df["Hours/Value"] = pd.to_numeric(df["Hours/Value"].replace("", "0"), errors="coerce").fillna(0.0)
    df["Contrib"] = pd.to_numeric(df["Contrib"].replace("", "0"), errors="coerce").fillna(0.0)
    df["Addition"] = pd.to_numeric(df["Addition"].replace("", "0"), errors="coerce").fillna(0.0)
    df["Code"] = df["Code"].astype(str).str.strip()

    # Intermediate dump for debugging
    df.to_csv('Intermediate_Output.csv', index=False)

    # --------------------------------------------------------------------------------
    # TOTAL calculations (kept consistent with your logic)
    # --------------------------------------------------------------------------------
    # For Super lines: codes 9, 8, CBUS, SUPER
    df['Total'] = np.where(
        (df["Code"].isin(["9", "8", "CBUS", "SUPER"])) & (df["Contrib"] == 0) & (df["Hours/Value"] != 0),
        (df["Pay Rate"] / 100.0) * df["Hours/Value"],
        np.where(
            (df["Code"].isin(["9", "8", "CBUS", "SUPER"])) & (df["Hours/Value"] == 0),
            df["Pay Rate"],
            np.where(
                (df["Code"].isin(["9", "8", "CBUS", "SUPER"])) & (df["Contrib"] != 0) & (df["Hours/Value"] != 0),
                df["Contrib"],
                df["Total"]  # leave unchanged otherwise
            )
        )
    )

    # Multiplicative totals for specific codes when Contrib == 0
    df['Total'] = np.where(
        (df["Code"].isin(["HRSBNS", "AL-CASHO", "KM10"])) & (df["Contrib"] == 0) & (df["Hours/Value"] != 0),
        df["Pay Rate"] * df["Hours/Value"],
        df["Total"]
    )

    # Codes where Total equals Addition (e.g., Salary Sacrifice, Public Holiday)
    df['Total'] = np.where(
        (df["Code"].isin(["SACRIFIC", "PH"])),
        df["Addition"],
        df["Total"]
    )

    # NORMTAX: Total = Pay Rate (%) of Hours/Value
    df["Total"] = np.where(
        (df["Code"] == "NORMTAX"),
        (df["Pay Rate"] / 100.0) * df["Hours/Value"],
        df["Total"]
    )

    # Date conversions
    df['Period Ending'] = pd.to_datetime(df['Period Ending'], errors='coerce')

    # Example override (kept from your code)
    df['Total'] = np.where(
        (df["Code"] == "9") & (df['Pay No.'] == '83061') & (df['Code_'] == 'SATS'),
        -8.37,
        df['Total']
    )

    return df

# ------------------------------------------------------------------------------------
# Run parser & downstream steps
# ------------------------------------------------------------------------------------
P1 = process_payroll_file(Text_part1)
P1.to_csv('P1Test.csv', index=False)

# Copy for rate processing
df_with_rates = P1.copy()

print(df_with_rates.dtypes)

# Build earliest pay rate changes per Full Name
df_normal = df_with_rates[df_with_rates["Code"] == "NORMAL"].copy()

# Ensure datetime
df_normal["Period Ending"] = pd.to_datetime(df_normal["Period Ending"], errors="coerce")

# Drop duplicates to avoid multiple same-rate entries on same day
df_unique = df_normal.drop_duplicates(subset=["Full Name", "Pay Rate", "Period Ending"])

# Earliest period for each Full Name & Pay Rate
earliest_rate_change = df_unique.groupby(["Full Name", "Pay Rate"])["Period Ending"].min().reset_index()
earliest_rate_change = earliest_rate_change.sort_values(["Full Name", "Period Ending"])
earliest_rate_change['Pay Rate'] = pd.to_numeric(earliest_rate_change['Pay Rate'], errors='coerce').round(2)

print("Earliest Pay Rate Changes by Full Name and Period Ending:")
print(earliest_rate_change)
earliest_rate_change.to_excel("Earliest_Pay_Rate_Changes.xlsx", index=False)

# Drop blank rows across key columns
columns_to_check = ['Code_', 'Full Name', 'Pay No.', 'Line', 'Code', 'Description']
df_with_rates[columns_to_check] = df_with_rates[columns_to_check].replace(r'^\s*$', np.nan, regex=True)
df_with_rates = df_with_rates.dropna(subset=columns_to_check, how='all')

# Convert to datetime and sort for merge_asof
df_with_rates["Period Ending"] = pd.to_datetime(df_with_rates["Period Ending"], errors="coerce")
earliest_rate_change["Period Ending"] = pd.to_datetime(earliest_rate_change["Period Ending"], errors="coerce")

df_sorted = df_with_rates.sort_values(by=["Period Ending", "Full Name"]).reset_index(drop=True)
earliest_rate_change_sorted = earliest_rate_change.sort_values(by=["Period Ending", "Full Name"]).reset_index(drop=True)

print(df_sorted["Period Ending"].dtype)
print(earliest_rate_change_sorted["Period Ending"].dtype)
print(df_sorted['Full Name'].dtype)
print(earliest_rate_change_sorted['Full Name'].dtype)

# Merge-as-of to get effective rate at each line date for the person
df_with_rates = pd.merge_asof(
    df_sorted,
    earliest_rate_change_sorted,
    on="Period Ending",
    by="Full Name",
    direction="backward",
    suffixes=("", "_Effective")
)

print("DF with rate columns: ")
print(df_with_rates.columns)
# print(df_with_rates.values)  # uncomment if you want to see raw

# Ensure numerics
df_with_rates['Hours/Value'] = pd.to_numeric(df_with_rates["Hours/Value"], errors='coerce').fillna(0.0)
df_with_rates['Pay Rate_Effective'] = pd.to_numeric(df_with_rates["Pay Rate_Effective"], errors='coerce').fillna(0.0)
df_with_rates['Pay Rate'] = pd.to_numeric(df_with_rates['Pay Rate'], errors='coerce').fillna(0.0)

# If you want date-only
df_with_rates["Period Ending"] = pd.to_datetime(df_with_rates["Period Ending"], errors="coerce").dt.date

# Recalculate LOAD totals using matched effective pay rate
df_with_rates["Total"] = np.where(
    df_with_rates["Code"] == "LOAD",
    ((df_with_rates["Pay Rate_Effective"] * df_with_rates['Pay Rate'] / 100.0) * df_with_rates['Hours/Value']),
    df_with_rates["Total"]
)

# Final rounding
df_with_rates['Total'] = df_with_rates['Total'].apply(safe_round)

# Output
df_with_rates.to_csv('With_Rates.csv', index=False)

print("Parsing complete. Files written: Intermediate_Output.csv, P1Test.csv, Earliest_Pay_Rate_Changes.xlsx, With_Rates.csv")