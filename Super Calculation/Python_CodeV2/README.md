# Maritimo Superannuation Guarantee (SG) Analysis Scripts

## Overview

There are **two scripts** in this folder. Both validate Superannuation Guarantee contributions for **Maritimo** (two entities: **MARITIMO LABOUR** and **MARITIMO OFFSHORE**). They compare expected SG (based on pay codes and ATO rates) against actual SG paid, flag discrepancies, and produce consolidated reports.

---

## Script Differences

| Aspect | `v0.3_Condensed Commentary.py` | `v1.5_Payroll Tax Recs.py` |
|---|---|---|
| **Core focus** | Pure SG discrepancy analysis + detailed commentary | SG discrepancies + **payroll tax classification** |
| **Client Mapping gating** | `No_OTE_paycodesBigBoats` list + `Effective_To`/`Effective_From` date window (inverts mapping outside window) | Simple `isin(OTE_paycodesBigBoats)` — no date gating |
| **MCB years** | FY2021–FY2026 (incl. FY2025 $65,070, FY2026 $62,500) | FY2021–FY2024 only (stops at $62,270) |
| **Exception dates** | Handles `21/12/2023` as a special one-off Super payment | Not handled |
| **"Above Cap" override** | Recalculates all 3 discrepancies from capped SG columns when above MCB | Not present |
| **Discrepancy columns** | `Underpayment Comments` / `Overpayment Comments` split (4 cols for Disc 1 & 2) | Plain single columns (`Discrepancy 1 - SW Comment`, etc.) |
| **Discrepancy Category** | Classifies rows into category + under/over | Not present |
| **Paycode Summary stage** | Not present | Groups by PayCode, classifies tax/Super/SALSAC/Child/Tax eligibility |
| **Extra input CSVs** | None | 6 additional: Allowances, Contributions, Deductions, Income cross-entity + Employee_Labels |
| **Comment analytics** | Not present | Produces `unique_comments.csv` with counts and in-depth tracing |
| **Excel output** | `client_payroll_analysis.xlsx` with formatting | No Excel file |
| **Extra CSV outputs** | None | `Paycode_Summary_new_input_file_fullFYs.csv`, `unique_comments.csv`, `Discp1_unique_QtrEMPLID.csv` |
| **Refer-to footnotes** | Appends "Refer to ..." in Disc 3 comments | Not present |

### Which one to run?

- Run **main - Only Super Calculationsv0.3_Condensed Commentary.py** if you only need the SG compliance check with a formatted Excel deliverable.
- **V0.3 was used for previous output sent to the client and the latest file shared with the team**

- Run **main v1.5 - Payroll Tax Recs.py** if you also need payroll tax classification, paycode-level summaries, and comment analytics.

Both use the same `dataframes.py` and mapping file — core payroll numbers will match.

---

## Data Flow

```
input\ (source CSVs)  -->  Python Script  -->  data\ (output results)
```

All input paths are relative to `Super Calculation\input\`. Source files from OneDrive should be placed in the following folder structure. The scripts write results to `Super Calculation\data\` (auto-created on first run). All output CSVs are **overwritten** each run, so copy any files you want to keep before re-running.

```
Super Calculation\
├── input\
│   ├── LABOUR
│   │   ├── Payroll\          ← payroll .csv files
│   │   ├── Super\            ← super .csv files
│   │   └── Employee_Labels.csv   (v1.5 only)
│   ├── OFFSHORE
│   │   ├── Payroll\          ← payroll .csv files
│   │   ├── Super\            ← super .csv files
│   │   └── Employee_Labels.csv   (v1.5 only)
│   ├── PAYCODE_MAPPING
│   │   └── 2.06.2026_PAYCODE_MAPPING.xlsx
│   ├── Allowances_crossEntity.csv   (v1.5 only)
│   ├── Contributions_crossEntity.csv (v1.5 only)
│   ├── Deductions_crossEntity.csv   (v1.5 only)
│   └── Income_crossEntity.csv       (v1.5 only)
└── data\                       ← auto-created, outputs written here
```

## Setting Up Input Data

**Source:** All source files have been stored in the team sharepoint - link sent seperately 
```

```

**Steps:**

1. **Payroll CSVs** — Export from the payroll system for each financial year. The script reads **all** `.csv` files in the folder, so you can drop in one combined file or multiple split files. Expected naming: `*PayrollTest_combined.csv`.

2. **Super CSVs** — Export super contribution data per entity. Place in the corresponding `Super\` subfolder.

3. **Paycode Mapping** — Copy the latest mapping spreadsheet from OneDrive. The script expects `2.06.2026_PAYCODE_MAPPING.xlsx` with a sheet named `UPDATED MAPPING`.

4. **Employee Labels (v1.5 only)** — Optional CSV with employee classification data. If missing, the script still runs but skips this enrichment.

5. **Cross-Entity CSVs (v1.5 only)** — Files like `Allowances_crossEntity.csv` etc. If you don't need payroll tax classification, use v0.3 instead and skip these.

**Quick checklist before running:**
- [ ] At least one `.csv` file in each `Payroll\` folder
- [ ] At least one `.csv` file in each `Super\` folder
- [ ] Mapping xlsx exists at `input\PAYCODE_MAPPING\`
- [ ] All CSVs use `latin1` encoding (standard export from their payroll system)
- [ ] No trailing whitespace issues — the script handles this automatically

## Input Data Sources (all under `Super Calculation\input\`)

| Source | Location |
|--------|----------|
| Payroll CSVs (Labour) | `input\LABOUR\Payroll\` |
| Payroll CSVs (Offshore) | `input\OFFSHORE\Payroll\` |
| Super CSVs (Labour) | `input\LABOUR\Super\` |
| Super CSVs (Offshore) | `input\OFFSHORE\Super\` |
| Paycode Mapping | `input\PAYCODE_MAPPING\2.06.2026_PAYCODE_MAPPING.xlsx` (sheet: `UPDATED MAPPING`) |
| Employee Labels | `input\{ENTITY}\Employee_Labels.csv` (v1.5 only) |
| Cross-Entity Files | `input\Allowances_crossEntity.csv`, `Contributions_crossEntity.csv`, `Deductions_crossEntity.csv`, `Income_crossEntity.csv` (v1.5 only) |

## Output Files (`Super Calculation\data\`)

### Common to both scripts

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

### v0.3 only

| File | Description |
|------|-------------|
| `client_payroll_analysis.xlsx` | **Main deliverable** — 3 sheets: *Qtr_Discrepancy_Results*, *Pay_Number_Summary*, *Payroll Detail* |

### v1.5 only

| File | Description |
|------|-------------|
| `Paycode_Summary_new_input_file_fullFYs.csv` | Paycode-level summary with tax/Super/SALSAC/Child classification |
| `unique_comments.csv` | Comment analytics with counts by type and in-depth tracing |
| `Discp1_unique_QtrEMPLID.csv` | Filtered discrepancy breakout by employee-quarter |

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

### v0.3 — Condensed Commentary (SG compliance + Excel output)

```powershell
python "Super Calculation\Python_CodeV2\main - Only Super Calculationsv0.3_Condensed Commentary.py"
```

### v1.5 — Payroll Tax Recs (SG + payroll tax + comment analytics)

```powershell
python "Super Calculation\Python_CodeV2\main v1.5 - Payroll Tax Recs.py"
```

**Requires:** `pandas`, `numpy`, `openpyxl`, `xlsxwriter`

## Notes

- Pay codes with descriptions flagged as adjustments/corrections (BACKPAY, UNPAID, CORRECTION, etc.) are excluded.
- A defined set of employee names is also excluded (apprentices, contractors, terminated staff).
- Input paths point to `Super Calculation\input\` — drop the source files into the structure shown above before running.
- The mapping file `2.06.2026_PAYCODE_MAPPING.xlsx` changed 6 paycodes from OTE to S&W compared to the previous `1.06.2026` version (Casual Bonus, Bonus By Hours, Leave Loading Term Pay, Long Service Leave Term, and two Workers Comp codes), reducing SW OTE by ~$890K.
