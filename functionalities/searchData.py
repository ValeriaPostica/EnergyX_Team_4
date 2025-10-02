import pandas as pd
import glob
import os
from datetime import datetime, timedelta


def find_highest_energy_difference(house_id, target_date):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    path = os.path.join(repo_root, 'data')
    try:
        target_date_obj = datetime.strptime(target_date, '%d.%m.%Y')
    except ValueError:
        print("Invalid date format. Please use DD.MM.YYYY format.")
        return None, None, None, None, None

    all_data = []

    data_files = [f for f in glob.glob(os.path.join(path, "*"))
                  if f.lower().endswith(('.csv', '.xlsx', '.xls'))]

    for file in data_files:
        try:
            if file.lower().endswith('.csv'):
                df = pd.read_csv(file, header=None, dtype=str, encoding='utf-8', on_bad_lines='skip')
            else:
                df = pd.read_excel(file, header=None, dtype=str)

            df.columns = ['id', 'datetime', 'active_energy_import', 'active_energy_export', 'transFullCoef', 'empty'][:len(df.columns)]

            # Convert id to numeric and filter by house_id
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
            df = df.dropna(subset=['id'])
            df = df[df['id'] == house_id]

            if not df.empty:
                df['datetime_obj'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
                df = df.dropna(subset=['datetime_obj'])

                df['active_energy_import'] = df['active_energy_import'].str.replace(',', '.').astype(float, errors='ignore')
                df = df.dropna(subset=['active_energy_import'])

                # Filter by target date
                df = df[df['datetime_obj'].dt.date == target_date_obj.date()]

                if not df.empty:
                    all_data.append(df)

        except Exception as e:
            print(f"Error processing file {file}: {e}")
            continue

    if not all_data:
        print(f"No data found for house ID {house_id} on date {target_date}")
        return None, None, None, None, None

    combined_data = pd.concat(all_data)

    combined_data = combined_data.drop_duplicates(subset=['datetime_obj'], keep='first')

    combined_data = combined_data.sort_values('datetime_obj').reset_index(drop=True)

    if len(combined_data) < 2:
        print("Need at least 2 measurements to calculate differences")
        return None, None, None, None, None

    interval_configs = [
        {'type': '15-minute', 'min_sec': 840, 'max_sec': 960, 'target_minutes': 15},
        {'type': '30-minute', 'min_sec': 1680, 'max_sec': 1920, 'target_minutes': 30},
        {'type': '1-hour', 'min_sec': 3300, 'max_sec': 3900, 'target_minutes': 60},
        {'type': 'any-interval', 'min_sec': 60, 'max_sec': 86400, 'target_minutes': None} 
    ]

    best_differences = []
    best_interval_type = None

    for config in interval_configs:
        differences = []
        valid_pairs = 0

        for i in range(len(combined_data) - 1):
            current = combined_data.iloc[i]
            next_point = combined_data.iloc[i + 1]

            time_gap = (next_point['datetime_obj'] - current['datetime_obj']).total_seconds()

            if config['min_sec'] <= time_gap <= config['max_sec']:
                energy_diff = next_point['active_energy_import'] - current['active_energy_import']

                if energy_diff > 0:
                    differences.append({
                        'interval_start': current['datetime_obj'],
                        'interval_end': next_point['datetime_obj'],
                        'energy_difference': energy_diff,
                        'energy_start': current['active_energy_import'],
                        'energy_end': next_point['active_energy_import'],
                        'actual_minutes': time_gap / 60,
                        'interval_type': config['type']
                    })
                    valid_pairs += 1

        if differences:
            best_differences = differences
            best_interval_type = config['type']
            break

    if not best_differences:
        print("No valid intervals with positive energy differences found")

        # Try absolute differences as fallback
        abs_differences = []
        for i in range(len(combined_data) - 1):
            current = combined_data.iloc[i]
            next_point = combined_data.iloc[i + 1]

            time_gap = (next_point['datetime_obj'] - current['datetime_obj']).total_seconds()
            energy_diff = abs(next_point['active_energy_import'] - current['active_energy_import'])

            if energy_diff > 0 and 60 <= time_gap <= 7200: 
                abs_differences.append({
                    'interval_start': current['datetime_obj'],
                    'interval_end': next_point['datetime_obj'],
                    'energy_difference': energy_diff,
                    'energy_start': current['active_energy_import'],
                    'energy_end': next_point['active_energy_import'],
                    'actual_minutes': time_gap / 60,
                    'interval_type': 'absolute-difference'
                })

        if abs_differences:
            best_differences = abs_differences
            best_interval_type = 'absolute-difference'
        else:
            print("No valid intervals found with absolute differences")
            return None, None, None, None, None

    max_diff = max(best_differences, key=lambda x: x['energy_difference'])

    return (max_diff['interval_start'], max_diff['interval_end'],
            max_diff['energy_difference'], best_interval_type, "Multiple files")


def analyze_energy_data_structure(house_id, target_date):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    path = os.path.join(repo_root, 'data')
    try:
        target_date_obj = datetime.strptime(target_date, '%d.%m.%Y')

        data_files = [f for f in glob.glob(os.path.join(path, "*"))
                      if f.lower().endswith(('.csv', '.xlsx', '.xls'))]

        for file in data_files[:1]:  # Just check first file for structure
            try:
                if file.lower().endswith('.csv'):
                    # Read without delimiter for separate columns
                    sample_df = pd.read_csv(file, header=None, dtype=str, nrows=5)
                else:
                    sample_df = pd.read_excel(file, header=None, dtype=str, nrows=5)


            except Exception as e:
                print(f"Error analyzing file {file}: {e}")
                continue

    except Exception as e:
        print(f"Analysis error: {e}")


def interactive_search():
    try:
        house_id = int(input("Enter house ID: ").strip())
        target_date = input("Enter date (DD.MM.YYYY format): ").strip()

        analyze_energy_data_structure(house_id, target_date)

        start_time, end_time, max_diff, interval_type, filename = find_highest_energy_difference(house_id, target_date)

        if start_time is not None and max_diff > 0:
            print(f"House ID: {house_id}")
            print(f"Date: {target_date}")
            print(f"Time interval: {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
            print(f"Energy difference: {max_diff:.3f} kWh")

            time_diff_hours = (end_time - start_time).total_seconds() / 3600
        else:
            print("\nError: No valid data found or no positive energy differences detected.")

    except ValueError:
        print("Invalid input! House ID must be a number.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    interactive_search()