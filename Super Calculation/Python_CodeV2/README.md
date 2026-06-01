# Maritimo Superannuation Guarantee (SG) Analysis Script

## Overview

This script validates Superannuation Guarantee contributions for **Maritimo** (two entities: **MARITIMO LABOUR** and **MARITIMO OFFSHORE**). It compares expected SG (based on pay codes and ATO rates) against actual SG paid, flags discrepancies, and produces a consolidated Excel report with commentary.

## Data Flow

```
input\ (source CSVs)  -->  Python Script  -->  data\ (output results)
```

All input paths are relative to `Super Calculation\input\`. Source files from OneDrive should be placed in the following folder structure:

```
Super Calculation\input\
├── LABOUR
│   ├── Payroll\          ← payroll .csv files
│   └── Super\            ← super .csv files
├── OFFSHORE
│   ├── Payroll\          ← payroll .csv files
│   └── Super\            ← super .csv files
└── PAYCODE_MAPPING
    └── 1.06.2026_PAYCODE_MAPPING.xlsx
```

## Input Data Sources (all under `Super Calculation\input\`)

| Source | Location |
|--------|----------|
| Payroll CSVs (Labour) | `input\LABOUR\Payroll\` |
| Payroll CSVs (Offshore) | `input\OFFSHORE\Payroll\` |
| Super CSVs (Labour) | `input\LABOUR\Super\` |
| Super CSVs (Offshore) | `input\OFFSHORE\Super\` |
| Paycode Mapping | `input\PAYCODE_MAPPING\1.06.2026_PAYCODE_MAPPING.xlsx` (sheet: `UPDATED MAPPING`) |

## Output Files (`Super Calculation\data\`)

| File | Description |
|------|-------------|
| `Payroll_Labour_data_load.csv` | Raw merged payroll (intermediate) |
| `payroll_data_LABOUR.csv` / `payroll_data_OFFSHORE.csv` | Enriched payroll with SG calcs |
| `Quarterly_payroll_data_LABOUR.csv` / `Quarterly_payroll_data_OFFSHORE.csv` | Aggregated by employee/quarter |
| `Payroll_Detail.csv` | Combined quarterly detail with discrepancy flags |
| `Quarterly_Sum.csv` | Pay-number level summary |
| `SG_Quarterly_Combined.csv` | Quarter-level SG reconciliation |
| `SG_Quarterly_BothEntities.csv` | Combined entity quarter results |
| `combined_result_with_comments.csv` | Final results with commentary |
| `client_payroll_analysis.xlsx` | **Main deliverable** — 3 sheets: *Qtr_Discrepancy_Results*, *Pay_Number_Summary*, *Payroll Detail* |

## Key Business Logic

1. **Financial Year & Quarters** — Australian FY (Jul–Jun). Includes a Labour-specific exception: pay periods on/after 28 June 2024 roll into Q1 of the next FY.
2. **SG Rates** — Hard-coded per FY (9.5% in FY21 stepping to 12% in FY26).
3. **Paycode Mapping** — Each pay code is classified via a mapping spreadsheet:
   - **Client Mapping** — codes flagged `Y` for SG by the client's own classification
   - **SW Mapping** — codes mapped to OTE, S&W, SUPER - SG, or TAX
4. **MCB (Maximum Contribution Base)** — Quarterly OTE caps applied per FY (ranging from $57,090 in FY21 to $65,070 in FY26).
5. **Three Discrepancies Computed:**
   - **D1:** Client Map expected SG vs SW Map expected SG (mapping differences)
   - **D2:** Client Map expected SG vs actual SG paid (client under/over payment)
   - **D3:** SW Map expected SG vs actual SG paid (compliance view)
6. **Commentary** — Automated categorisation (underpayment, overpayment, no super paid, mapping issue). Discrepancies within ±$0.08 are deemed immaterial.
7. **Materiality** — Differences under $0.08 are suppressed as noise.

## How to Run

```powershell
python "Super Calculation\Python_CodeV2\main - Only Super Calculationsv0.3_Condensed Commentary.py"
```

Requires: `pandas`, `numpy`, `openpyxl`, `xlsxwriter`

## Notes

- Pay codes with descriptions flagged as adjustments/corrections (BACKPAY, UNPAID, CORRECTION, etc.) are excluded.
- A defined set of employee names is also excluded (apprentices, contractors, terminated staff).
- Input paths point to `Super Calculation\input\` — drop the source files into the structure shown above before running.
