import pandas as pd
import numpy as np
import datetime
import random # slightly varied mock consumer data

# All of this is mock data for now,

def get_report_data(start_date, end_date):
    MOCK_CONTOUR_IDS = [
        13836498, 14098248, 14101503, 14101511, 14101513, 
        14101530, 14101590, 14101593, 14101607, 14101611,
        14101619, 14212364, 14270112, 14270128, 14270160, 
        14286724, 14381537, 14381538, 14381539, 14381540
    ]
    
    MOCK_USAGE_VALUES = [43, 43, 43, 45, 45, 44, 44, 47, 47, 44, 44, 44, 44, 43, 43, 45, 45, 45, 45]
    
    MOCK_REGIONS = [
        "Balti", "Cahul", "Chisinau", "Comrat", "Cricova", 
        "Edinet", "Floresti", "Hincesti", "Orhei", "Rezina", 
        "Soroca", "Stefan Voda", "Tiraspol", "Ungheni", "Vadul lui Voda"
    ]
    
    TARIFF_RATE = 0.10
        
    # 1. Reconstruct Time Series (for Charting)
    # Assuming MOCK_USAGE_VALUES are hourly readings, create a timestamp index
    num_readings = len(MOCK_USAGE_VALUES)
    
    # Ensure start_date is a datetime object for pd.date_range
    try:
        start_dt = pd.to_datetime(start_date)
    except ValueError:
        # Fallback if date string is bad
        start_dt = datetime.datetime.now()
        
    timestamps = pd.date_range(start=start_dt, periods=num_readings, freq='H') 
    
    # DataFrame for the chart (Total Consumption over Time)
    df_timeseries = pd.DataFrame({
        'timestamp': timestamps,
        'kwh_total': MOCK_USAGE_VALUES
    })

    # 2. Top Consumer Data (NECESSARY ASSUMPTION)
    # We must arbitrarily assign usage to consumer IDs to satisfy the 'Top 10' metric.
    
    consumer_ids = MOCK_CONTOUR_IDS
    if not consumer_ids or not MOCK_USAGE_VALUES:
        df_consumers = pd.DataFrame(columns=['contour_id', 'kwh', 'cost'])
    else:
        # Use a list of usage values that totals roughly the same as the total usage
        # and assign a usage value to each consumer ID, slightly randomized
        total_mock_usage = sum(MOCK_USAGE_VALUES)
        
        # Arbitrarily assign consumption to each consumer
        consumer_kwh_list = [
            (total_mock_usage / len(consumer_ids)) * (1 + random.uniform(-0.1, 0.5)) 
            for _ in consumer_ids
        ]
        
        df_consumers = pd.DataFrame({
            'contour_id': consumer_ids,
            'kwh': consumer_kwh_list,
        })
        df_consumers['cost'] = df_consumers['kwh'] * TARIFF_RATE


    # 3. Calculate Totals and Aggregations
    
    # The total consumption for the report period is the sum of the time series
    total_kwh = sum(MOCK_USAGE_VALUES)
    total_cost = total_kwh * TARIFF_RATE

    # 4. Get Top 10 Consumers (Group by ID, sum kwh and cost, sort)
    
    # Since we generated one total usage per consumer, the groupby is straightforward
    top_consumers_agg = df_consumers.groupby('contour_id')[['kwh', 'cost']].sum()
    
    top_consumers = (
        top_consumers_agg.sort_values('kwh', ascending=False)
        .head(10)
        .reset_index()
        .to_dict('records')
    )

    # 5. Return the required components
    return {
        "df_raw": df_timeseries, # For the chart: timestamp and total kwh
        "total_kwh": total_kwh,
        "total_cost": total_cost,
        "top_consumers": top_consumers, # List of dicts for the table
        "regions": MOCK_REGIONS # List of regions for the regional average metric
    }