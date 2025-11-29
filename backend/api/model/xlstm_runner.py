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
import matplotlib

# Robust import of get_series whether run as package or standalone script
try:
    from ..retrieve_data import get_series  # type: ignore
except ImportError:  # running as a script directly (no parent package)
    import sys
    _CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    _API_DIR = os.path.dirname(_CURRENT_DIR)  # backend/api
    if _API_DIR not in sys.path:
        sys.path.append(_API_DIR)
    from retrieve_data import get_series

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

# -----------------------------------------------------------------------------
# Device-aware forecasting
# -----------------------------------------------------------------------------

DEVICE_INCREASE_MAP = {
    "light": 3,
    "thermostat": 10.6,
    "conditioner": 20.0,
}

DEVICE_DECREASE_MAP = {
    "energy_saving": -25.0,
}

### PARAMETERS TO TUNE DEVICE EFFECTS

REBOUND_FACTOR = 0.3  # fraction of the device increase applied negatively for 1 step after turning off

# Soft post-peak decay (no hard caps): when no increasing devices are active,
# gently pull predictions toward the recent mean to model natural relaxation
# after peaks. Tune rate in [0,1]; 0 disables, higher pulls faster.
DECAY_RATE = 0.45  # 25% of the surplus over recent mean per step
CAP_NO_DEVICES = 200.0  # max increase over last value when no devices active
CAP_WITH_DEVICES = 500.0  # max increase over last value when devices active

def _expand_schedule(schedule: List[tuple], n: int) -> dict:
    """Convert a list of (device, start_hour, end_hour) into boolean activation arrays.

    Hours are inclusive of end (e.g., ("thermostat", 12, 15) activates 12,13,14,15).
    Out-of-range hours are clipped to [0, n-1].
    """
    activity: dict = {}
    for device, start, end in schedule:
        arr = activity.setdefault(device, np.zeros(n, dtype=bool))
        if end < start:
            continue
        s = max(0, int(start))
        e = min(n - 1, int(end))
        arr[s : e + 1] = True
    return activity

@torch.no_grad()
def forecast_user_with_devices(series: np.ndarray, n: int, schedule: List[tuple]) -> List[float]:
    """Forecast with device schedule adjustments.

    schedule: List of (device_name, start_hour, end_hour) relative to forecast horizon.
    Devices: light, thermostat, conditioner (increase); energy_saving (decrease).
        Adjustment strategy:
      1. Compute base model prediction per step.
      2. Sum increases for active devices + decreases for energy_saving.
            3. Apply rebound (negative adjustment) the hour immediately after an increasing device turns off.
            4. Apply gentle mean-reversion toward recent mean when no increasing devices are active (no hard caps).
      4. Cap per-step increase over previous value (different caps when devices active vs not).
    """
    base_series = np.array(series, dtype=np.float32)
    preds: List[float] = []
    ckpt = torch.load(MODEL_PATH, map_location="cpu")
    h = ckpt["hyper"]
    lookback = int(h["lookback"])
    if not h.get("ctx_norm", False):
        raise ValueError("Checkpoint not trained with context normalization; retrain with the provided trainer.")
    if base_series.shape[0] < lookback:
        raise ValueError(f"Need at least lookback={lookback} points; got {base_series.shape[0]}")

    device = _get_device()
    model = LSTMForecaster(
        input_size=h["input_size"],
        hidden_size=h["hidden_size"],
        num_layers=h["num_layers"],
        dropout=h["dropout"],
    ).to(device)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    activity = _expand_schedule(schedule, n)
    prev_active: set = set()
    ctx = base_series.copy()

    eps = 1e-8
    for step in range(n):
        window = ctx[-lookback:]
        mu = float(np.mean(window))
        sd = float(np.std(window))
        s = sd if sd > eps else 1.0
        x_norm = ((window - mu) / s).astype(np.float32)[:, None]
        x_t = torch.from_numpy(x_norm).unsqueeze(0).to(device)
        base_pred_norm = model(x_t).item()
        base_pred = base_pred_norm * s + mu

        # Active devices this hour
        active_devices = {d for d, arr in activity.items() if arr[step]}
        increases = sum(DEVICE_INCREASE_MAP.get(d, 0.0) for d in active_devices)
        decreases = sum(DEVICE_DECREASE_MAP.get(d, 0.0) for d in active_devices)
        adjustment = increases + decreases

        # Rebound: devices that were active last hour but now off
        turned_off = prev_active - active_devices
        for d in turned_off:
            inc_val = DEVICE_INCREASE_MAP.get(d)
            if inc_val:
                adjustment -= REBOUND_FACTOR * inc_val

        candidate = base_pred + adjustment

        # Soft post-peak decay (mean reversion) when no increasing devices are active
        if DECAY_RATE > 0 and increases <= 0:
            # Use the same normalization window mean "mu" as the short-term baseline
            if candidate > mu:
                candidate -= DECAY_RATE * (candidate - mu)
        last_val = float(ctx[-1])

        cap = CAP_WITH_DEVICES if increases > 0 else CAP_NO_DEVICES
        diff = candidate - last_val
        if diff > cap:
            candidate = last_val + cap

        # Ensure non-negative
        if candidate < 0:
            candidate = 0.0

        preds.append(float(candidate))
        ctx = np.append(ctx, candidate).astype(np.float32)
        prev_active = active_devices

    return preds

def m_eval_devices(series: np.ndarray, schedule: List[tuple], week: bool = False) -> List[float]:
    """Device-aware evaluation wrapper.

    schedule: list of (device, start_hour, end_hour) relative to forecast horizon.
    week=True -> 168 hour horizon, else 24.
    """
    horizon = 168 if week else 24
    print("DEBUG: device-aware user forecast")
    return forecast_user_with_devices(series, horizon, schedule)


def plot_m_eval_devices(
    series: np.ndarray,
    schedule: List[tuple],
    week: bool = False,
    save_path: str | None = None,
    title: str = "Device-Aware Forecast",
    history_max: int | None = None,
):
    """Quick visualization for m_eval_devices.

    - Plots provided history and the device-adjusted forecast.
    - Shades forecast region where devices are active.
    - Requires matplotlib; imported lazily to avoid hard dependency at import time.
    """
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception as e:
        print("Matplotlib not available. Install with: pip install matplotlib")
        print(f"Plot skipped. Reason: {e}")
        return None

    hist = np.asarray(series, dtype=float)
    forecast = m_eval_devices(hist, schedule, week=week)
    n = len(forecast)

    # Optionally trim very long history for visibility
    if history_max is not None and len(hist) > history_max:
        hist = hist[-history_max:]

    hist_x = np.arange(len(hist))
    fut_x = np.arange(len(hist), len(hist) + n)

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(hist_x, hist, label="History", color="#1f77b4")
    ax.plot(fut_x, forecast, label="Forecast", color="#ff7f0e")

    # Vertical separator between history and forecast
    ax.axvline(len(hist) - 0.5, color="gray", linestyle="--", linewidth=1, alpha=0.8)

    # Shade device activity during forecast horizon
    activity = _expand_schedule(schedule, n)
    color_map = {
        "light": "#f5f5a6",
        "thermostat": "#ffcccc",
        "conditioner": "#cce5ff",
        "energy_saving": "#d4edda",
    }

    labeled = set()
    for device, arr in activity.items():
        if not np.any(arr):
            continue
        color = color_map.get(device, "#dddddd")
        start = None
        for i, active in enumerate(arr):
            if active and start is None:
                start = i
            # segment ends when we hit an inactive slot or at last index
            last_index = (i == n - 1)
            if (not active or last_index) and start is not None:
                end = i if last_index and active else i - 1
                ax.axvspan(len(hist) + start, len(hist) + end + 1, color=color, alpha=0.15,
                           label=(f"{device} active" if device not in labeled else None))
                labeled.add(device)
                start = None

    ax.set_title(title)
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Usage")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="best")
    fig.tight_layout()

    if save_path:
        try:
            fig.savefig(save_path, dpi=150)
            print(f"Saved plot to: {save_path}")
        except Exception as e:
            print(f"Failed to save figure: {e}")

    try:
        plt.show()
    except Exception:
        # Non-interactive environment
        pass

    return forecast


if __name__ == "__main__":
    # Example: thermostat on 12-15, conditioner 13-16, lights 18-22, energy saving 0-5
    example_schedule = [
        ("thermostat", 12, 15),
        ("conditioner", 13, 16),
        ("light", 8, 20),
        ("energy_saving", 18, 21),
    ]

    series_1 = get_series(13836498, 1)
    series_2 = get_series(13836498, 2)
    series_3 = get_series(13836498, 3)
    series_4 = get_series(13836498, 4)
    series_5 = get_series(13836498, 5)
    series = (series_1 + series_2 + series_3 + series_4 + series_5)
    print(series)

    # Dummy initial series for demonstration (replace with real user history)
    init_series = np.linspace(10, 20, 88, dtype=np.float32)
    forecast = m_eval_devices(series, example_schedule, week=False)
    print("Device-aware forecast (24h):", forecast)

    plot_m_eval_devices(series, example_schedule, week=False, save_path=None, history_max=168)