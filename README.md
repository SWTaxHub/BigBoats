# Super Guarantee & Payroll Tax Analysis

## Setting Up Input Data

Before running either script, ensure the following data directories and files exist:

```
BigBoats/
├── input/
│   ├── PAYCODE_MAPPING_v1.xlsx       # Pay code mapping (v1.5 script)
│   ├── PAYCODE_MAPPING_v2.xlsx       # Pay code mapping (v0.3 script)
│   ├── excluded_employees.csv         # Employees to exclude from calculations
│   ├── Awards/
│   │   └── 5.Award Coverage *.csv
│   ├── LABOUR/
│   │   ├── Employee_Labels.xlsx       # Employee details (payroll data joins)
│   │   └── Employee_Labels.csv        # Same data in CSV format
│   └── OFFSHORE/
│       └── Employee_Labels.xlsx       # Offshore employee details
├── data/                              # Output files land here
└── Super Calculation/
    └── input/
        ├── LABOUR/
        │   └── Payroll data.xlsx      # Labour payroll transactions
        └── OFFSHORE/
            └── Payroll data.xlsx      # Offshore payroll transactions
```

File paths are defined in `Super Calculation/dataframes.py` using `os.path.join(os.path.dirname(__file__), ...)` so they resolve relative to the project root.

## Scripts Overview

**`main v1.5 - Payroll Tax Recs.py`**
- Used for payroll tax reconciliation
- Uses pay code mapping v1 (`PAYCODE_MAPPING_v1.xlsx`)
- Outputs: quarterly OTE/S&W totals, SG calculations, discrepancy reports
- Focused on comparing client-provided mapping vs SW mapping at the pay code level

**`main - Only Super Calculationsv0.3_Condensed Commentary.py`**
- Used for superannuation guarantee quarterly calculations
- Uses pay code mapping v2 (`PAYCODE_MAPPING_v2.xlsx`)
- Outputs: same quarterly structure plus overpayment/underpayment commentary per employee
- Adds date gating (effective from/to) so only active pay codes contribute
- Excludes specific pay codes (`No_OTE_paycodesBigBoats`) from OTE calculation

## Why Two Scripts?

The two scripts evolved for different purposes:

| | v1.5 (Payroll Tax) | v0.3 (Condensed Commentary) |
|---|---|---|
| **Purpose** | Payroll tax return preparation | Super guarantee reconciliation |
| **Mapping version** | v1 (2025.10.04) | v2 (2.06.2026) |
| **Date gating** | No | Yes |
| **Over/underpayment comments** | No | Yes |
| **Runs from** | Annual/quarterly payroll tax work | Monthly super guarantee cycles |

The v0.3 script is the more detailed version — it was extended from v1.5 to handle super-specific requirements like date-effective pay codes and employee-level commentary. Over time the mapping files also diverged as different pay code classifications were needed for payroll tax vs super guarantee purposes.
