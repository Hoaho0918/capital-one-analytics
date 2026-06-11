import os
import sys
import uuid
from datetime import datetime
import pandas as pd

# Add project root directory to path to allow importing from src.quality
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.quality.tests import initialize_audit_tables, log_pipeline_run, run_bronze_checks

def ingest_to_bronze(source_file_path: str, output_directory: str):
    print("--- PIPELINE DIAGNOSTICS ---")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for source file at: {os.path.abspath(source_file_path)}")
    
    if os.path.exists("data"):
        print(f"Contents of 'data/': {os.listdir('data')}")
        if os.path.exists("data/bronze"):
            print(f"Contents of 'data/bronze/': {os.listdir('data/bronze')}")
    else:
        print("CRITICAL: The root 'data' folder does not exist in your repository!")
    print("--------------------------------\n")

    if not os.path.exists(source_file_path):
        raise FileNotFoundError(f"PIPELINE CRASHED: The file '{source_file_path}' does not exist in your repository. Please upload your CSV to data/bronze/ first!")
        
    print(f"Starting Ingestion for: {source_file_path}")
    df = pd.read_csv(source_file_path, dtype=str)
    
    df['ingested_at'] = datetime.utcnow().isoformat()
    df['source_file'] = os.path.basename(source_file_path)
    df['batch_id'] = str(uuid.uuid4())
    
    os.makedirs(output_directory, exist_ok=True)
    output_filename = "bronze_raw_landing.csv"
    final_output_path = os.path.join(output_directory, output_filename)
    df.to_csv(final_output_path, index=False)
    
    print(f"Ingestion successful! Stored data at: {final_output_path}")
    return final_output_path

if __name__ == "__main__":
    # Your verified lowercase data path configurations
    RAW_DATA_SOURCE = "data/bronze/sampledataset.csv"
    BRONZE_LANDING_ZONE = "data/bronze/"
    
    # Start Audit Framework Logging Session
    initialize_audit_tables()
    pipeline_run_uuid = str(uuid.uuid4())
    start_time = datetime.utcnow().isoformat()
    
    try:
        # Run Ingestion
        saved_bronze_file = ingest_to_bronze(RAW_DATA_SOURCE, BRONZE_LANDING_ZONE)
        
        # Run quality test check immediately following file creation
        run_bronze_checks(pipeline_run_uuid, saved_bronze_file)
        
        # Log successful run metrics to audit tables
        log_pipeline_run(pipeline_run_uuid, "BRONZE", "SUCCESS", start_time)
        print("Bronze Layer build and quality validations complete.")
        
    except Exception as e:
        # Catch errors and document system crashes automatically
        log_pipeline_run(pipeline_run_uuid, "BRONZE", "FAILED", start_time, error_msg=str(e))
        print(f"Pipeline Ingestion Failed: {str(e)}")
        raise e
