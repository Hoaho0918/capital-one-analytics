import os
import json
import uuid
import pandas as pd
from datetime import datetime, timezone

AUDIT_RUNS_PATH = "data/audit/pipeline_runs.csv"
AUDIT_CHECKS_PATH = "data/audit/data_quality_checks.csv"

def initialize_audit_tables():
    os.makedirs("data/audit", exist_ok=True)
    if not os.path.exists(AUDIT_RUNS_PATH):
        df_runs = pd.DataFrame(columns=["run_id", "layer", "status", "started_at", "completed_at", "error_message"])
        df_runs.to_csv(AUDIT_RUNS_PATH, index=False)
        
    if not os.path.exists(AUDIT_CHECKS_PATH):
        df_checks = pd.DataFrame(columns=["check_id", "run_id", "layer", "test_name", "target_column", "status", "failure_count", "checked_at"])
        df_checks.to_csv(AUDIT_CHECKS_PATH, index=False)

def log_pipeline_run(run_id, layer, status, started_at, error_msg=""):
    df = pd.read_csv(AUDIT_RUNS_PATH)
    new_run = pd.DataFrame([{
        "run_id": run_id,
        "layer": layer,
        "status": status,
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "error_message": error_msg
    }])
    pd.concat([df, new_run]).to_csv(AUDIT_RUNS_PATH, index=False)

def log_test_result(run_id, layer, test_name, column, status, failure_count):
    df = pd.read_csv(AUDIT_CHECKS_PATH)
    new_check = pd.DataFrame([{
        "check_id": str(uuid.uuid4()),
        "run_id": run_id,
        "layer": layer,
        "test_name": test_name,
        "target_column": column,
        "status": status,
        "failure_count": int(failure_count),
        "checked_at": datetime.now(timezone.utc).isoformat()
    }])
    pd.concat([df, new_check]).to_csv(AUDIT_CHECKS_PATH, index=False)

def run_bronze_checks(run_id, bronze_path):
    print(f"🕵️ Running Bronze Integrity Gates for: {bronze_path}")
    df = pd.read_csv(bronze_path, dtype=str)
    
    required_metadata = ['ingested_at', 'source_file', 'batch_id']
    missing_cols = [c for c in required_metadata if c not in df.columns]
    log_test_result(
        run_id, 
        "BRONZE", 
        "required_metadata_columns_exist", 
        "ALL", 
        "PASS" if not missing_cols else "FAIL", 
        len(missing_cols)
    )

def log_dbt_test_results(run_id, dbt_project_target_path, layer_name):
    run_results_file = os.path.join(dbt_project_target_path, 'target', 'run_results.json')
    
    print(f"📦 Scanning dbt Test Artifacts for {layer_name} at: {run_results_file}")
    
    if not os.path.exists(run_results_file):
        print(f"⚠️ Warning: Could not find dbt run_results.json at {run_results_file}")
        return
        
    with open(run_results_file, 'r') as f:
        dbt_data = json.load(f)
        
    for result in dbt_data.get('results', []):
        unique_id = result.get('unique_id', 'unknown_test')
        
        test_name = unique_id.split('.')[-1] 
        
        dbt_status = result.get('status', 'FAIL').upper()
        status = "PASS" if dbt_status == "PASS" else "FAIL"
        
        failures = result.get('failures', 0)
        if failures is None:
            failures = 0
            
        log_test_result(
            run_id=run_id,
            layer=layer_name,
            test_name=test_name,
            column="DBT_ASSERTION",
            status=status,
            failure_count=failures
        )
        
    print(f"✅ Successfully compiled {layer_name} dbt test schemas into central audit ledger.")
