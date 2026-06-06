import os
import uuid
from datetime import datetime
import pandas as pd

def ingest_to_bronze(source_file_path: str, output_directory: str):
    if not os.path.exists(source_file_path):
        raise FileNotFoundError(f"Source file not found at: {source_file_path}")
        
    print(f"Starting Ingestion for: {source_file_path}")
    
    # Read raw data as strings to preserve the exact raw state
    df = pd.read_csv(source_file_path, dtype=str)
    
    # Append the 3 required pipeline tracking columns
    df['ingested_at'] = datetime.utcnow().isoformat()
    df['source_file'] = os.path.basename(source_file_path)
    df['batch_id'] = str(uuid.uuid4())
    
    os.makedirs(output_directory, exist_ok=True)
    
    # Save as a clean CSV in the bronze folder
    output_filename = "bronze_raw_landing.csv"
    final_output_path = os.path.join(output_directory, output_filename)
    df.to_csv(final_output_path, index=False)
    
    print(f"Ingestion successful! Stored data at: {final_output_path}")

if __name__ == "__main__":
    # Pointing to the location of your uploaded sample file
    RAW_DATA_SOURCE = "data/bronze/sampledataset.csv"
    BRONZE_LANDING_ZONE = "data/bronze/"
    ingest_to_bronze(RAW_DATA_SOURCE, BRONZE_LANDING_ZONE)

