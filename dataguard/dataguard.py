import pandas as pd
import sqlite3
import os
from datetime import datetime

print("=" * 60)
print("  DATAGUARD - Research Application Validation Pipeline")
print("=" * 60)

# Load the CSV
df = pd.read_csv("applications.csv")
print(f"\n Total applications received: {len(df)}")

# Track issues
errors = []
clean_rows = []

for index, row in df.iterrows():
    row_errors = []

    # Check 1: Duplicate application ID
    if df['application_id'].tolist().count(row['application_id']) > 1:
        row_errors.append("DUPLICATE application ID")

    # Check 2: Missing applicant name
    if pd.isna(row['applicant_name']) or str(row['applicant_name']).strip() == "":
        row_errors.append("MISSING applicant name")

    # Check 3: Missing email
    if pd.isna(row['email']) or str(row['email']).strip() == "":
        row_errors.append("MISSING email")

    # Check 4: Missing project title
    if pd.isna(row['project_title']) or str(row['project_title']).strip() == "":
        row_errors.append("MISSING project title")

    # Check 5: Funding over limit
    if pd.notna(row['funding_requested']) and float(row['funding_requested']) > 150000:
        row_errors.append(f"FUNDING EXCEEDS LIMIT (${row['funding_requested']:,.0f} > $150,000)")

    if row_errors:
        errors.append({
            "application_id": row['application_id'],
            "applicant_name": row['applicant_name'],
            "issues": " | ".join(row_errors)
        })
    else:
        clean_rows.append(row)

# Save clean data to SQL database
clean_df = pd.DataFrame(clean_rows)
conn = sqlite3.connect("dataguard.db")
clean_df.to_sql("approved_applications", conn, if_exists="replace", index=False)
conn.close()

# Save error report to CSV
error_df = pd.DataFrame(errors)
error_df.to_csv("error_report.csv", index=False)

# Print summary
print(f"\n Clean records loaded to database: {len(clean_rows)}")
print(f" Rejected records with issues:     {len(errors)}")
print("\n--- FLAGGED APPLICATIONS ---")
for e in errors:
    print(f"\n  ID    : {e['application_id']}")
    print(f"  Name  : {e['applicant_name']}")
    print(f"  Issues: {e['issues']}")

print("\n" + "=" * 60)
print("  Error report saved  → error_report.csv")
print("  Clean data saved    → dataguard.db")
print("=" * 60)
print(f"\n  Pipeline completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")