import pandas as pd
import glob
import os
from datetime import datetime, timedelta


def get_all_unique_ids():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    repo_root = os.path.dirname(script_dir)
    path = os.path.join(repo_root, 'data')

    unique_ids = set()
    data_files = [f for f in glob.glob(os.path.join(path, "*"))
                  if f.lower().endswith(('.csv', '.xlsx', '.xls'))]

    for file in data_files:
        try:
            if file.lower().endswith('.csv'):
                df = pd.read_csv(file, header=None, dtype=str, encoding='utf-8', on_bad_lines='skip')
            else:
                df = pd.read_excel(file, header=None, dtype=str)

            if len(df.columns) > 0:
                id_column = df.iloc[:, 0]
                numeric_ids = pd.to_numeric(id_column, errors='coerce')
                valid_ids = numeric_ids.dropna().astype(int)
                unique_ids.update(valid_ids.tolist())
                
        except Exception as e:
            print(f"Error processing file {file}: {e}")
            continue

    return sorted(unique_ids)


def calculate_total_unique_ids():
    """Calculate and display the sum of all unique IDs"""
    unique_ids = get_all_unique_ids()
    
    # if not unique_ids:
    #     print("No unique IDs found in any files.")
    #     return
    
    
    print(len(unique_ids))

if __name__ == "__main__":
    calculate_total_unique_ids()