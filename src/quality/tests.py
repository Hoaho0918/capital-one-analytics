import os
import uuid
import pandas as pd
from datetime import datetime

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
