import os

# Test the path resolution (simulating being in backend/api/model/)
SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")  # Simulate being in model/
API_DIR = os.path.dirname(SCRIPT_DIR)                    # backend/api/
BACKEND_DIR = os.path.dirname(API_DIR)                   # backend/
MODEL_DATA_DIR = os.path.join(BACKEND_DIR, "data", "model_data")
MODEL_PATH = os.path.join(MODEL_DATA_DIR, "model.pt")
DATA_PATH = os.path.join(MODEL_DATA_DIR, "processed.json")

print(f"SCRIPT_DIR: {SCRIPT_DIR}")
print(f"API_DIR: {API_DIR}")
print(f"BACKEND_DIR: {BACKEND_DIR}")
print(f"MODEL_DATA_DIR: {MODEL_DATA_DIR}")
print(f"MODEL_PATH: {MODEL_PATH}")
print(f"DATA_PATH: {DATA_PATH}")

print(f"\nModel file exists: {os.path.exists(MODEL_PATH)}")
print(f"Data file exists: {os.path.exists(DATA_PATH)}")