import os
import uuid
import json
from datetime import datetime
import pandas as pd

AUDIT_RUNS_PATH = "data/audit/pipeline_runs.csv"
AUDIT_CHECKS_PATH = "data/audit/data_quality_checks.csv"

def initialize_audit_tables():
    """Ensures audit storage tracking files exist with correct schemas."""
    os.makedirs("data/audit", exist_ok=True)
    
    if not os.path.exists(AUDIT_RUNS_PATH):
        df_runs = pd.DataFrame(columns=["run_id", "layer", "status", "started_at", "completed_at", "error_message"])
        df_runs.to_csv(AUDIT_RUNS_PATH, index=False)
        
    if not os.path.exists(AUDIT_CHECKS_PATH):
        df_checks = pd.DataFrame(columns=["check_id", "run_id", "layer", "test_name", "target_column", "status", "failure_count", "checked_at"])
        df_checks.to_csv(AUDIT_CHECKS_PATH, index=False)

def log_pipeline_run(run_id, layer, status, started_at, error_msg=""):
    """Appends high-level orchestration health statuses to pipeline_runs."""
    df = pd.read_csv(AUDIT_RUNS_PATH)
    new_run = pd.DataFrame([{
        "run_id": run_id, "layer": layer, "status": status,
        "started_at": started_at, "completed_at": datetime.utcnow().isoformat(),
        "error_message": error_msg
    }])
    pd.concat([df, new_run]).to_csv(AUDIT_RUNS_PATH, index=False)

def log_test_result(run_id, layer, test_name, column, status, failure_count):
    """Appends granular assertions and row anomalies to data_quality_checks."""
    df = pd.read_csv(AUDIT_CHECKS_PATH)
    new_check = pd.DataFrame([{
        "check_id": str(uuid.uuid4()), "run_id": run_id, "layer": layer,
        "test_name": test_name, "target_column": column, "status": status,
        "failure_count": int(failure_count), "checked_at": datetime.utcnow().isoformat()
    }])
    pd.concat([df, new_check]).to_csv(AUDIT_CHECKS_PATH, index=False)

def run_bronze_checks(run_id, bronze_path):
    """Assertions immediately following the raw landing zone ingestion."""
    print(f"🕵️ Running Bronze Integrity Gates for: {bronze_path}")
    df = pd.read_csv(bronze_path, dtype=str)
    
    # Check 1: Required system tracking columns exist
    required_metadata = ['ingested_at', 'source_file', 'batch_id']
    missing_cols = [c for c in required_metadata if c not in df.columns]
    log_test_result(
        run_id, "BRONZE", "required_metadata_columns_exist", "ALL",
        "PASS" if not missing_cols else "FAIL", len(missing_cols)
    )

def run_silver_checks(run_id, customer_df, account_df, loan_df, bronze_path):
    """Business condition validations and cross-layer row count reconciliation."""
    print("🕵️ Running Silver Quality Assertions...")
    
    # Check 2: Customer Primary Keys are not null
    null_cust_ids = customer_df['customer_id'].isna().sum()
    log_test_result(run_id, "SILIVER", "customer_id_not_null", "customer_id", "PASS" if null_cust_ids == 0 else "FAIL", null_cust_ids)

    # Check 3: Age is within rational human boundary parameters (18 - 110)
    invalid_ages = customer_df[~customer_df['customer_age'].between(18, 110, inclusive='both') & customer_df['customer_age'].notna()].shape[0]
    log_test_result(run_id, "SILVER", "age_in_bounds", "customer_age", "PASS" if invalid_ages == 0 else "FAIL", invalid_ages)

    # Check 4: Loan volumes are strictly positive numbers
    negative_loans = loan_df[loan_df['loan_amount'] < 0].shape[0]
    log_test_result(run_id, "SILVER", "loan_amount_positive", "loan_amount", "PASS" if negative_loans == 0 else "FAIL", negative_loans)

    # Check 5: Primary Keys are deduplicated completely
    duplicate_accounts = account_df.duplicated(subset=['account_id']).sum()
    log_test_result(run_id, "SILVER", "account_id_unique", "account_id", "PASS" if duplicate_accounts == 0 else "FAIL", duplicate_accounts)

    # Check 6: Row count reconciliation between source records and transformations
    df_bronze_total = pd.read_csv(bronze_path, dtype=str).shape[0]
    silver_distinct_customers = customer_df['customer_id'].nunique()
    discrepancy = abs(df_bronze_total - silver_distinct_customers)
    
    # Since it's an aggregation reconciliation tracking logs, failure count is the discrepancy gap
    log_test_result(run_id, "SILVER", "row_count_reconciliation", "customer_id", "PASS" if discrepancy == 0 else "WARNING", discrepancy)

if __name__ == "__main__":
    initialize_audit_tables()
    print("✅ Quality framework initialized. Integrated dynamically inside execution tasks.")

