import os
import uuid
from datetime import datetime
import pandas as pd

def ingest_to_bronze(source_file_path: str, output_directory: str):
    # --- DEBUG HELPERS ---
    print("--- PIPELINE DIAGNOSTICS ---")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for source file at: {os.path.abspath(source_file_path)}")
    
    # Check if data/ folder exists at all, and list what is inside it
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

if __name__ == "__main__":
    RAW_DATA_SOURCE = "data/bronze/sampledataset.csv"
    BRONZE_LANDING_ZONE = "data/bronze/"
    ingest_to_bronze(RAW_DATA_SOURCE, BRONZE_LANDING_ZONE)
