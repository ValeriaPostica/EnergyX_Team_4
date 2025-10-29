# eval_lstm_panel.py
# Load a pretrained global LSTM and forecast n steps for a selected user.
# Usage:
#   python eval_lstm_panel.py --model model.pt --data processed.json --user 0 --n 24
#
# Prints the forecast list.

from __future__ import annotations
import argparse, json
from typing import List
import os
import random

# -----------------------------------------------------------------------------
# Set BLAS/threading env vars BEFORE importing numpy/torch to avoid
# nondeterministic parallel reductions and cross-platform variation.
# -----------------------------------------------------------------------------
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("BLIS_NUM_THREADS", "1")

import numpy as np
import torch
from torch import nn

# Get the correct paths to the model files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/api/model/
API_DIR = os.path.dirname(SCRIPT_DIR)                    # backend/api/
BACKEND_DIR = os.path.dirname(API_DIR)                   # backend/
MODEL_DATA_DIR = os.path.join(BACKEND_DIR, "data", "model_data")
MODEL_PATH = os.path.join(MODEL_DATA_DIR, "model.pt")

# -----------------------------------------------------------------------------
# Determinism & seeding
# -----------------------------------------------------------------------------
# Environment-configurable, with sensible defaults for reproducibility.
SEED = int(os.getenv("MODEL_SEED", "44"))
# Force CPU by default to avoid CUDA nondeterminism differences across machines.
FORCE_CPU = os.getenv("MODEL_FORCE_CPU", "1") != "0"

def _init_determinism() -> None:
    """
    Make PyTorch/NumPy/Python RNG deterministic and configure backends.

    Notes:
    - We set CUBLAS_WORKSPACE_CONFIG for CUDA determinism, but we also default to
      CPU inference (FORCE_CPU) to guarantee identical results across runs.
    - Torch deterministic algorithms are enabled. Some ops may raise if no
      deterministic implementation exists; we pass warn_only=True where supported.
    - We also limit thread counts to reduce potential non-deterministic
      accumulation order differences in parallel kernels on some BLAS backends.
    """
    # Best-effort CUDA determinism env; must be set before CUDA context creation.
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":16:8")

    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)

    try:
        # torch>=1.8
        torch.use_deterministic_algorithms(True, warn_only=True)
    except TypeError:
        # older torch versions
        torch.use_deterministic_algorithms(True)

    # cuDNN settings (safe on CPU as well)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # Limit threading to stabilize floating-point accumulation order
    try:
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
    except Exception:
        pass


def _get_device() -> torch.device:
    if FORCE_CPU:
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Initialize determinism as soon as the module is imported.
_init_determinism()

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
    ckpt = torch.load(MODEL_PATH, map_location="cpu")
    h = ckpt["hyper"]
    lookback = int(h["lookback"])
    if not h.get("ctx_norm", False):
        raise ValueError("Checkpoint not trained with context normalization; retrain with the provided trainer.")
    if series.shape[0] < lookback:
        raise ValueError(f"Need at least lookback={lookback} points; got {series.shape[0]}")

    # Select device with determinism preference.
    device = _get_device()
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

# Quick eval of the integer sequence 0..24
def m_eval(series: np.ndarray = [], week: bool = False) -> List[float]:
    """
    If location == -1: interpret user_index as USER row in processed.json
    If location != -1: interpret user_index as REGION row in processed_regions.json
    """
    horizon = 168 if week else 24
    print(f"DEBUG: user forecast")
    return forecast_user(series, horizon)


if __name__ == "__main__":
    print("Returned", m_eval(week=True, location=0))
