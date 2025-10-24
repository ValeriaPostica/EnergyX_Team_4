# eval_lstm_panel.py
# Load a pretrained global LSTM and forecast n steps for a selected user.
# Usage:
#   python eval_lstm_panel.py --model model.pt --data processed.json --user 0 --n 24
#
# Prints the forecast list.

from __future__ import annotations
import argparse, json
from typing import List
import numpy as np
import torch
from torch import nn

import os

"""
    Commit app.py and other files and merge with main branch before this file
"""


# Get the correct paths to the model files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/api/model/
API_DIR = os.path.dirname(SCRIPT_DIR)                    # backend/api/
BACKEND_DIR = os.path.dirname(API_DIR)                   # backend/
MODEL_DATA_DIR = os.path.join(BACKEND_DIR, "data", "model_data")
MODEL_PATH_OLD = os.path.join(MODEL_DATA_DIR, "model_old.pt")
MODEL_PATH_NEW = os.path.join(MODEL_DATA_DIR, "model.pt")
USER_DATA_PATH = os.path.join(MODEL_DATA_DIR, "processed.json")
LOCAL_DATA_PATH = os.path.join(MODEL_DATA_DIR, "processed_regions.json")


# --------------------------- IO ---------------------------
def load_array2d(path: str) -> np.ndarray:
    if path.endswith(".npy"):
        arr = np.load(path)
    else:
        with open(path, "r", encoding="utf-8") as f:
            arr = np.array(json.load(f), dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D array [U, T], got shape {arr.shape}")
    return arr.astype(np.float32)

# --------------------------- Model ---------------------------
class GlobalLSTMForecaster(nn.Module):
    def __init__(self, num_users: int, input_size: int, hidden_size: int,
                 num_layers: int, id_embed_dim: int, dropout: float):
        super().__init__()
        self.use_id = id_embed_dim > 0
        self.id_embed = nn.Embedding(num_users, id_embed_dim) if self.use_id else None
        self.lstm = nn.LSTM(
            input_size=input_size + (id_embed_dim if self.use_id else 0),
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Linear(hidden_size, 1)
    def forward(self, x: torch.Tensor, user_ids: torch.Tensor | None = None):
        if self.use_id:
            if user_ids is None:
                raise ValueError("user_ids required when id_embed_dim>0")
            emb = self.id_embed(user_ids)
            emb_rep = emb.unsqueeze(1).expand(-1, x.size(1), -1)
            x = torch.cat([x, emb_rep], dim=-1)
        out, _ = self.lstm(x)
        last = out[:, -1, :]
        return self.head(last)

# --------------------------- Forecast ---------------------------

class LSTMForecaster(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, dropout=0.1):
        super().__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers,
                            batch_first=True, dropout=dropout if num_layers > 1 else 0.0)
        self.head = nn.Linear(hidden_size, 1)
    def forward(self, x: torch.Tensor):
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :])

@torch.no_grad()
def forecast_user(series: np.ndarray, n: int) -> List[float]:
    series = np.array(series, dtype=np.float32)
    ckpt = torch.load(MODEL_PATH_NEW, map_location="cpu")
    h = ckpt["hyper"]
    lookback = int(h["lookback"])
    if not h.get("ctx_norm", False):
        raise ValueError("Checkpoint not trained with context normalization; retrain with the provided trainer.")
    if series.shape[0] < lookback:
        raise ValueError(f"Need at least lookback={lookback} points; got {series.shape[0]}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LSTMForecaster(
        input_size=h["input_size"],
        hidden_size=h["hidden_size"],
        num_layers=h["num_layers"],
        dropout=h["dropout"],
    ).to(device)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    eps = 1e-8
    ctx = series.astype(np.float32).copy()   # work in original units
    preds: List[float] = []

    for _ in range(n):
        window = ctx[-lookback:]
        mu = float(np.mean(window))
        sd = float(np.std(window))
        s = sd if sd > eps else 1.0

        x_norm = ((window - mu) / s).astype(np.float32)[:, None]   # [L,1]
        x_t = torch.from_numpy(x_norm).unsqueeze(0).to(device)     # [1,L,1]
        yhat_norm = model(x_t).item()
        yhat = yhat_norm * s + mu                                  # back to original units

        preds.append(float(yhat))
        ctx = np.append(ctx, yhat).astype(np.float32)

    return preds


ckpt = torch.load(MODEL_PATH_OLD, map_location="cpu")
local_data = load_array2d(LOCAL_DATA_PATH)             # [R, T] regions x time

@torch.no_grad()
def forecast_region_series(ckpt_path: str, data_path: str, region_idx: int, n: int) -> List[float]:
    """Forecast n steps for a single region series using its own mean/std,
    while feeding a constant embedding id=0 just to satisfy the model."""
    hyper = ckpt["hyper"]
    lookback = hyper["lookback"]
    U_saved  = hyper["num_users"]  # users _in training_, needed for embedding size

    R, T = local_data.shape
    if region_idx < 0 or region_idx >= R:
        raise IndexError(f"region index {region_idx} out of range 0..{R-1}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = GlobalLSTMForecaster(
        num_users=U_saved,
        input_size=hyper["input_size"],   # should be 1
        hidden_size=hyper["hidden_size"],
        num_layers=hyper["num_layers"],
        id_embed_dim=hyper["id_embed_dim"],
        dropout=hyper["dropout"],
    ).to(device)
    model.load_state_dict(ckpt["state_dict"], strict=True)
    model.eval()

    # Use region's own scaler (not checkpoint scalers)
    series = local_data[region_idx]                # [T]
    if T <= lookback:
        raise ValueError(f"Series length {T} must be > lookback={lookback}")

    # Optional: if your deltas can be spiky/negative due to meter resets, you may clip:
    # series = np.clip(series, 0, None)

    mu = float(series.mean())
    sd = float(series.std())
    s  = sd if sd > 1e-8 else 1.0

    window = ((series[-lookback:] - mu) / s).astype(np.float32)       # [L]
    window_t = torch.from_numpy(window).unsqueeze(0).unsqueeze(-1).to(device)  # [1,L,1]

    # Feed a fixed embedding id (e.g., 0). It won't semantically match a "region",
    # but keeps the dimensions valid. For best results, retrain on regions.
    uid_t = torch.tensor([0], dtype=torch.long, device=device)

    preds_scaled = []
    for _ in range(n):
        yhat = model(window_t, uid_t).item()
        preds_scaled.append(yhat)
        next_step = torch.tensor([[[yhat]]], dtype=torch.float32, device=device)
        window_t = torch.cat([window_t[:, 1:, :], next_step], dim=1)

    preds = (np.array(preds_scaled, dtype=np.float32) * s + mu).tolist()
    return preds

# Quick eval of the integer sequence 0..24
def m_eval(series: np.ndarray = [], week: bool = False, location: int = -1) -> List[float]:
    """
    If location == -1: interpret user_index as USER row in processed.json
    If location != -1: interpret user_index as REGION row in processed_regions.json
    """
    horizon = 168 if week else 24
    if series != []:
        print(f"DEBUG: user forecast")
        return forecast_user(series, horizon)
    else:
        print(f"DEBUG: region forecast")
        return forecast_region_series(MODEL_PATH_OLD, LOCAL_DATA_PATH, location, horizon)


if __name__ == "__main__":
    print("Returned", m_eval(week=True, location=0))
