import pandas as pd
import ast

def model(dbt, session):
    # Reference your bronze raw landing data source
    # (If using a data warehouse source, replace this with dbt.source)
    df_raw = pd.read_csv("data/bronze/bronze_raw_landing.csv")
    
    flattened_rows = []
    
    # Safely unpack the string representations of dictionaries row-by-row
    for _, row in df_raw.iterrows():
        combined_dict = {}
        for col in df_raw.columns:
            val = row[col]
            if pd.isna(val) or str(val).strip() == "":
                continue
            # Parse string-dictionaries (e.g. "[{'transaction_id': ...}]" or "{'age': ...}")
            try:
                # If wrapped in a list '[{...}]', grab the first element
                parsed_val = ast.literal_eval(str(val))
                if isinstance(parsed_val, list) and len(parsed_val) > 0:
                    parsed_val = parsed_val[0]
                
                if isinstance(parsed_val, dict):
                    combined_dict.update(parsed_val)
                else:
                    combined_dict[col] = val
            except (ValueError, SyntaxError):
                # Fallback if the cell is a standard plain text string
                combined_dict[col] = val
                
        flattened_rows.append(combined_dict)
        
    # Convert our list of clean dictionaries back into a structured DataFrame
    df_flat = pd.DataFrame(flattened_rows)
    return df_flat
