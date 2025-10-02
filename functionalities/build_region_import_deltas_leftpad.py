import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# ---- Config ----
INPUT_PATH  = Path("data.json")                 # raw readings
MAP_PATH    = Path("meter_to_location.json")    # region -> [meter_ids]
OUT_SERIES  = Path("processed_regions.json")    # array-of-arrays
OUT_INDEX   = Path("regions_index.json")        # {"regions": ["Balti", "Chisinau", ...]}

CLOCK_COL  = "Clock (8:0-0:1.0.0*255:2)"
IMPORT_COL = "Active Energy Import (3:1-0:1.8.0*255:2)"
TIME_FMT   = "%d.%m.%Y %H:%M:%S"


# ---------- Helpers ----------
def _to_float(v: Any) -> float | None:
    """Robust float conversion; returns None if not parseable."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return None if (isinstance(v, float) and math.isnan(v)) else float(v)
    s = str(v).strip().replace(",", ".")
    if s == "":
        return None
    try:
        val = float(s)
        return None if math.isnan(val) else val
    except Exception:
        return None


def _parse_dt(s: str) -> datetime:
    return datetime.strptime(s, TIME_FMT)


def _normalize_input(data: Any) -> Dict[str, List[Dict[str, Any]]]:
    """
    Accept either:
      A) { meter_id: [ {Clock:..., Import:...}, ... ], ... }
      B) [ { "Meter": "...", Clock:..., Import:... }, ... ]
    Return dict: meter_id -> list of rows.
    """
    by_meter: Dict[str, List[Dict[str, Any]]] = {}

    if isinstance(data, dict):
        for meter_id, rows in data.items():
            if not isinstance(rows, list):
                continue
            clean = [r for r in rows if CLOCK_COL in r and IMPORT_COL in r]
            by_meter[str(meter_id)] = clean
    elif isinstance(data, list):
        for r in data:
            if "Meter" in r and CLOCK_COL in r and IMPORT_COL in r:
                m = str(r["Meter"])
                by_meter.setdefault(m, []).append(r)
    else:
        raise ValueError("Unsupported data.json format")
    return by_meter


def _compute_import_deltas(rows: List[Dict[str, Any]]) -> List[float]:
    """
    Sort by time; compute consecutive deltas: next - last for IMPORT_COL.
    If a pair has missing/unparseable values, that delta is skipped.
    """
    if not rows:
        return []
    rows_sorted = sorted(rows, key=lambda r: _parse_dt(r[CLOCK_COL]))
    vals: List[float | None] = [_to_float(r.get(IMPORT_COL)) for r in rows_sorted]

    deltas: List[float] = []
    for i in range(len(vals) - 1):
        v1, v2 = vals[i], vals[i + 1]
        if v1 is None or v2 is None:
            continue
        deltas.append(v2 - v1)
    return deltas


def _first_nonzero_or_default(seq: List[float], default: float = 0.0) -> float:
    for x in seq:
        if x is not None and x != 0.0:
            return float(x)
    return default


def _left_pad_nearest(seqs: List[List[float]]) -> List[List[float]]:
    """
    Make all sequences equal to the maximum length by *prepending*
    the nearest-member value:
      - Find the first non-zero value in the sequence; if none, use 0.
      - Prepend that value as many times as needed.
    """
    if not seqs:
        return seqs
    max_len = max(len(s) for s in seqs)
    out: List[List[float]] = []
    for s in seqs:
        need = max_len - len(s)
        if need <= 0:
            out.append(s)
            continue
        seed = _first_nonzero_or_default(s, default=0.0)
        out.append([seed] * need + s)
    return out


def _sum_series(series_list: List[List[float]], length: int) -> List[float]:
    """Elementwise sum; if list is empty, return zeros."""
    if not series_list:
        return [0.0] * length
    # assume all have `length`
    return [sum(vals) for vals in zip(*series_list)]


# ---------- Main ----------
def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")
    if not MAP_PATH.exists():
        raise FileNotFoundError(f"Mapping file not found: {MAP_PATH}")

    with INPUT_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    with MAP_PATH.open("r", encoding="utf-8") as f:
        region_to_meters_raw = json.load(f)

    # 1) Per-meter deltas
    by_meter = _normalize_input(raw)
    meter_ids_sorted = sorted(by_meter.keys(), key=lambda x: (len(x), x))
    per_meter_series: Dict[str, List[float]] = {}
    for m in meter_ids_sorted:
        per_meter_series[m] = _compute_import_deltas(by_meter[m])

    # 2) Left-pad all meters to max length (nearest-member extrapolation, prepend)
    max_len = max((len(s) for s in per_meter_series.values()), default=0)
    padded = _left_pad_nearest(list(per_meter_series.values()))
    for key, seq in zip(meter_ids_sorted, padded):
        per_meter_series[key] = seq

    # 3) Build region sums (each array = sum across its meters, elementwise)
    #    If a listed meter is missing, treat it as a zero-series.
    region_names = sorted(region_to_meters_raw.keys())
    zeros = [0.0] * max_len
    region_series: List[List[float]] = []
    for region in region_names:
        meters = region_to_meters_raw.get(region, [])
        # normalize ids to strings (mapping may contain ints)
        meters = [str(m) for m in meters]
        series_list = [per_meter_series.get(m, zeros) for m in meters]
        summed = _sum_series(series_list, max_len)
        region_series.append(summed)

    # 4) Write outputs
    with OUT_SERIES.open("w", encoding="utf-8") as f:
        json.dump(region_series, f, ensure_ascii=False, indent=2)
    with OUT_INDEX.open("w", encoding="utf-8") as f:
        json.dump({"regions": region_names}, f, ensure_ascii=False, indent=2)

    n = len(region_series)
    L = len(region_series[0]) if n else 0
    print(f"✓ Wrote {n} region series to {OUT_SERIES} (uniform length = {L}).")
    print(f"✓ Index written to {OUT_INDEX} (same order as arrays).")


if __name__ == "__main__":
    main()
