import pandas as pd
import sqlite3
import logging
import sys
from datetime import datetime
from pathlib import Path
from config import INPUT_FILE, DATABASE, ERROR_FILE, CLEAN_FILE, FUNDING_LIMIT, REQUIRED_COLUMNS

# ── Logging setup ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("dataguard.log")
    ]
)
log = logging.getLogger(__name__)

def load_data(filepath: str) -> pd.DataFrame:
    path = Path(filepath)
    if not path.exists():
        log.error(f"Input file not found: {filepath}")
        sys.exit(1)
    try:
        df = pd.read_csv(filepath)
        log.info(f"Loaded {len(df)} records from {filepath}")
        return df
    except Exception as e:
        log.error(f"Failed to read CSV: {e}")
        sys.exit(1)

def validate_columns(df: pd.DataFrame):
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        log.error(f"Missing required columns: {missing}")
        sys.exit(1)
    log.info("All required columns present")

def validate_records(df: pd.DataFrame):
    errors = []
    clean_rows = []
    seen_ids = set()

    for _, row in df.iterrows():
        row_errors = []

        if row["application_id"] in seen_ids:
            row_errors.append("DUPLICATE application ID")
        else:
            seen_ids.add(row["application_id"])

        if pd.isna(row["applicant_name"]) or str(row["applicant_name"]).strip() == "":
            row_errors.append("MISSING applicant name")

        if pd.isna(row["email"]) or str(row["email"]).strip() == "":
            row_errors.append("MISSING email")

        if pd.isna(row["project_title"]) or str(row["project_title"]).strip() == "":
            row_errors.append("MISSING project title")

        try:
            if float(row["funding_requested"]) > FUNDING_LIMIT:
                row_errors.append(f"FUNDING EXCEEDS LIMIT (${float(row['funding_requested']):,.0f} > ${FUNDING_LIMIT:,})")
        except (ValueError, TypeError):
            row_errors.append("INVALID funding amount")

        if row_errors:
            errors.append({
                "application_id": row["application_id"],
                "applicant_name": row["applicant_name"],
                "issues": " | ".join(row_errors)
            })
            log.warning(f"Rejected {row['application_id']}: {' | '.join(row_errors)}")
        else:
            clean_rows.append(row)

    return clean_rows, errors

def save_to_database(clean_df: pd.DataFrame):
    try:
        with sqlite3.connect(DATABASE) as conn:
            clean_df.to_sql("approved_applications", conn, if_exists="replace", index=False)
        log.info(f"Saved {len(clean_df)} clean records to {DATABASE}")
    except Exception as e:
        log.error(f"Database write failed: {e}")
        sys.exit(1)

def save_reports(clean_df: pd.DataFrame, errors: list):
    clean_df.to_csv(CLEAN_FILE, index=False)
    log.info(f"Clean dataset exported -> {CLEAN_FILE}")
    if errors:
        error_df = pd.DataFrame(errors)
        error_df.to_csv(ERROR_FILE, index=False)
        log.info(f"Error report exported -> {ERROR_FILE} ({len(errors)} records)")
    else:
        log.info("No errors found — error report not generated")

def print_summary(total: int, clean: list, errors: list):
    print("\n" + "=" * 60)
    print("  DATAGUARD PIPELINE SUMMARY")
    print("=" * 60)
    print(f"  Total received  : {total}")
    print(f"  Clean records   : {len(clean)}")
    print(f"  Rejected records: {len(errors)}")
    if errors:
        all_issues = " | ".join([e["issues"] for e in errors])
        print("\n  Error breakdown:")
        for label in ["DUPLICATE", "MISSING applicant", "MISSING email", "MISSING project", "FUNDING EXCEEDS", "INVALID funding"]:
            count = all_issues.count(label)
            if count:
                print(f"    {label:30s} → {count} record(s)")
    print("\n  Outputs:")
    print(f"    {CLEAN_FILE:30s} -> clean validated records")
    print(f"    {ERROR_FILE:30s} -> rejected with reason codes")
    print(f"    {DATABASE:30s} -> SQLite database")
    print(f"    dataguard.log{' '*17} -> full audit log")
    print("=" * 60)
    print(f"  Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def main():
    log.info("Starting DataGuard pipeline")
    df = load_data(INPUT_FILE)
    validate_columns(df)
    clean_rows, errors = validate_records(df)
    clean_df = pd.DataFrame(clean_rows)
    save_to_database(clean_df)
    save_reports(clean_df, errors)
    print_summary(len(df), clean_rows, errors)
    log.info("Pipeline completed successfully")

if __name__ == "__main__":
    main()