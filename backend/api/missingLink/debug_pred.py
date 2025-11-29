
import os
import sys
import torch
import numpy as np

# Add parent directory to path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from retrieve_data import get_series_country
from model.xlstm_runner import MODEL_PATH

def debug():
    print("Debugging prediction for Balti...")
    
    # 1. Check series length
    try:
        series = get_series_country("Balti")
        print(f"Series length for Balti: {len(series)}")
        if len(series) > 0:
            print(f"First 5 values: {series[:5]}")
            print(f"Last 5 values: {series[-5:]}")
    except Exception as e:
        print(f"Error getting series: {e}")
        return

    # 2. Check model lookback
    try:
        print(f"Loading model from {MODEL_PATH}")
        ckpt = torch.load(MODEL_PATH, map_location="cpu")
        h = ckpt["hyper"]
        lookback = int(h["lookback"])
        print(f"Model lookback: {lookback}")
        
        if len(series) < lookback:
            print(f"ERROR: Series length {len(series)} is less than lookback {lookback}")
        else:
            print("Series length is sufficient.")
            
    except Exception as e:
        print(f"Error loading model: {e}")

if __name__ == "__main__":
    debug()
