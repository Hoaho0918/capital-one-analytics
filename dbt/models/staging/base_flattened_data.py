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
        list_to_explode = None  # Temporary storage to hold multi-element lists

        # Step 1: Read and parse all columns for the current row
        for col in df_raw.columns:
            val = row[col]
            if pd.isna(val) or str(val).strip() == "":
                continue

            # Parse string-dictionaries or string-lists
            try:
                parsed_val = ast.literal_eval(str(val))
                
                if isinstance(parsed_val, list):
                    # Save the list to explode after all other columns are parsed
                    list_to_explode = parsed_val
                    
                elif isinstance(parsed_val, dict):
                    # Flatten single dictionaries immediately
                    combined_dict.update(parsed_val)
                    
                else:
                    # Keep basic data types (integers, floats, booleans)
                    combined_dict[col] = parsed_val
                    
            except (ValueError, SyntaxError):
                # Fallback if the cell is a standard plain text string
                combined_dict[col] = val

        # Step 2: Handle row distribution / explosion after parsing finishes
        if list_to_explode and len(list_to_explode) > 0:
            for item in list_to_explode:
                # Copy the base data so every item gets its own separate row
                new_row = combined_dict.copy()
                if isinstance(item, dict):
                    new_row.update(item)
                else:
                    # Fallback if the list item is a primitive type (e.g.)
                    new_row['list_value'] = item
                flattened_rows.append(new_row)
        else:
            # If there was no list in this row, save the baseline data normally
            flattened_rows.append(combined_dict)

    # Convert our list of clean dictionaries back into a structured DataFrame
    df_flat = pd.DataFrame(flattened_rows)
    return df_flat
