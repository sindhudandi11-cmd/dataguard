# DataGuard — Research Application Validation Pipeline

> An automated Python ETL pipeline that validates incoming grant applications against 5 business rules, saves clean records to a SQLite database, and auto-generates an error report for resubmission.

📦 **[GitHub](https://github.com/sindhudandi11-cmd/dataguard)**

---

## Problem

Research program coordinators manually review hundreds of incoming grant applications — catching duplicates, missing fields, and funding violations by hand. This is slow, inconsistent, and error-prone at scale.

## Solution

DataGuard automates the entire intake process. It ingests raw application data, validates every record against 5 business rules, saves only clean records to a SQLite database, and auto-generates a structured error report so coordinators know exactly what to fix and resubmit.

---

## Pipeline Integration

DataGuard is Part 1 of an integrated 3-system research data pipeline:

| System | Role | Repo |
|---|---|---|
| **DataGuard** | Validates and cleans bulk application data | This repo |
| **GrantViz** | Power BI dashboard fed by manually importing DataGuard's clean output CSV | [View Dashboard](https://app.powerbi.com/links/_Klk_n52xa?ctid=ea873390-8c1c-4231-a799-6b5a0235b2e6&pbi_source=linkShare&bookmarkGuid=1e74c21b-e973-4448-ba65-81103b101826) |
| **AppScan AI** | AI review system for real-time incoming submissions | [github.com/sindhudandi11-cmd/appscan](https://github.com/sindhudandi11-cmd/appscan) |

---

## Validation Rules

| # | Rule |
|---|---|
| 1 | Duplicate `application_id` detection — only the second occurrence is rejected |
| 2 | Missing `applicant_name` |
| 3 | Missing `email` address |
| 4 | Missing `project_title` |
| 5 | `funding_requested` exceeds $150,000 limit |

---

## Input Format

DataGuard expects a CSV or Excel file with the following columns:

| Column | Type | Required |
|---|---|---|
| `application_id` | String / Integer | ✅ Yes |
| `applicant_name` | String | ✅ Yes |
| `email` | String | ✅ Yes |
| `department` | String | No |
| `project_title` | String | ✅ Yes |
| `funding_requested` | Number | ✅ Yes |
| `start_date` | Date | No |
| `end_date` | Date | No |
| `institution` | String | No |

**Example input row:**

| application_id | applicant_name | email | department | project_title | funding_requested | start_date | end_date | institution |
|---|---|---|---|---|---|---|---|---|
| APP-001 | Dr. Sarah Chen | sarah.chen@msu.edu | AgBioResearch | Soil Microbiome Analysis | 45000 | 2026-01-01 | 2026-12-31 | Michigan State University |

A sample dataset is included in `sample_data/applications_sample.csv` to test the pipeline immediately after cloning.

---

## Output Files

| File | Description |
|---|---|
| `clean_applications.csv` | Validated records — manually imported into the GrantViz Power BI dashboard for visual reporting |
| `error_report.csv` | Rejected applications with exact reason codes for coordinator review |
| `dataguard.db` | SQLite database of approved records only |
| `dataguard.log` | Full audit log with timestamps at INFO / WARNING / ERROR levels |

---

## Results on Sample Dataset

| Metric | Count |
|---|---|
| Total applications processed | 101 |
| Clean records saved | 71 |
| Rejected with issues | 30 |

---

## Prerequisites

- Python 3.8 or higher
- pip

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sindhudandi11-cmd/dataguard.git
cd dataguard
```

### 2. Install dependencies

```bash
pip install pandas openpyxl
```

Or if a `requirements.txt` is present:

```bash
pip install -r requirements.txt
```

### 3. Add your input file

Place your CSV or Excel application file in the project root. Update the input file path in `config.py` if needed.

### 4. Run the pipeline

```bash
python dataguard.py
```

Outputs are written to the project root: `clean_applications.csv`, `error_report.csv`, `dataguard.db`, and `dataguard.log`.

---

## Development Notes

### v1.0 → v2.0 Improvements

During development I identified and resolved several issues through self-review against production pipeline standards:

| Issue Found | Fix Applied |
|---|---|
| Hardcoded config values buried in code | Extracted to `config.py` — business rules now configurable without touching pipeline logic |
| Duplicate detection flagged both records | Fixed using `seen_ids` set — only the second occurrence is rejected |
| `print()` statements throughout | Replaced with Python `logging` module — INFO/WARNING/ERROR levels saved to audit log |
| No error handling on file/DB operations | Added `try/except` with graceful failure messages |
| Database connection could leak on crash | Replaced with `with` statement for safe auto-close |
| `os` imported but never used | Removed dead import |

---

## Troubleshooting

**`FileNotFoundError` on run** — check that your input file path matches what is set in `config.py`. The file must be in the expected location before running.

**`KeyError` on a column name** — verify your input file has all required columns with exact spelling. Column names are case-sensitive.

**Empty `clean_applications.csv`** — check `error_report.csv` and `dataguard.log` to see which rules rejected all records. Likely a formatting issue in the input file.

**pandas `ImportError`** — run `pip install pandas openpyxl` and confirm you are using Python 3.8+.

---

## Technologies

Python · Pandas · SQLite · ETL · Business Process Automation

---

## Author

**Sindhu Dandibhatla** — [github.com/sindhudandi11-cmd](https://github.com/sindhudandi11-cmd) · [LinkedIn](https://www.linkedin.com/in/sindhudandi2/)

For bugs or feature requests, [open an issue](https://github.com/sindhudandi11-cmd/dataguard/issues).

---

*Licensed under the MIT License.*
