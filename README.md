# DataGuard — Research Application Validation Pipeline

## Problem
Research program coordinators manually review hundreds of incoming grant applications — catching duplicates, missing fields, and funding violations by hand. This is slow and error-prone.

## Solution
DataGuard is an automated Python pipeline that ingests raw application data, validates every record against 5 business rules, saves only clean records to a SQLite database, and auto-generates an error report for coordinators to fix and resubmit.

## Validation Rules
1. Duplicate application ID detection
2. Missing applicant name
3. Missing email address
4. Missing project title
5. Funding request exceeds $150,000 limit

## How to Run
1. Install dependencies:
   pip install pandas openpyxl

2. Run the pipeline:
   python dataguard.py

## Output Files
| File | Description |
|---|---|
| clean_applications.csv | Clean validated records — feeds into GrantViz Power BI dashboard |
| error_report.csv | Rejected applications with exact reason codes |
| dataguard.db | SQLite database of approved records only |
| dataguard.log | Full audit log with timestamps |

## Pipeline Integration
DataGuard is Part 1 of a 3-project data system:
- **DataGuard** → validates and cleans raw applications
- **GrantViz** → Power BI dashboard built on DataGuard's clean output
- **AppScan AI** → GenAI review system for incoming submissions

## Results on Sample Dataset
- Total applications processed: 101
- Clean records saved: 71
- Rejected with issues: 30

## Development Notes
### v1.0 → v2.0 Improvements
During development I identified and resolved several issues:

| Issue Found | Fix Applied |
|---|---|
| Hardcoded config values buried in code | Extracted to config.py — business rules now configurable without touching pipeline logic |
| Duplicate detection flagged both records | Fixed using seen_ids set — only second occurrence rejected |
| print() statements throughout | Replaced with Python logging module — INFO/WARNING/ERROR levels saved to audit log |
| No error handling on file/DB operations | Added try/except with graceful failure messages |
| Database connection could leak on crash | Replaced with `with` statement for safe auto-close |
| os imported but never used | Removed dead import |

These improvements reflect real-world code review feedback and production pipeline standards.

## Technologies
Python · Pandas · SQLite · ETL · Business Process Automation
