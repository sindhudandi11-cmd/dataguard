# DataGuard Configuration
# Modify these values to customize pipeline behavior

INPUT_FILE    = "applications.csv"
DATABASE      = "dataguard.db"
ERROR_FILE    = "error_report.csv"
CLEAN_FILE    = "clean_applications.csv"
FUNDING_LIMIT = 150000

REQUIRED_COLUMNS = {
    "application_id",
    "applicant_name",
    "email",
    "project_title",
    "funding_requested"
}