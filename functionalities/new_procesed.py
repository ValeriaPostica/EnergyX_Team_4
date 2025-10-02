import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# ---- Config ----
INPUT_PATH  = Path("data.json")
OUTPUT_PATH = Path("processed.json")

CLOCK_COL  = "Clock (8:0-0:1.0.0*255:2)"
IMPORT_COL = "Active Energy Import (3:1-0:1.8.0*255:2)"
TIME_FMT   = "%d.%m.%Y %H:%M:%S"


# ---------- Helpers ----------
def _to_float(v: Any) -> float | None:
    """Robust float conversion; returns None if not parseable."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        # convert NaN to None
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
    If either side of a pair is missing (unparseable), that delta is skipped.
    """
    if not rows:
        return []
    rows_sorted = sorted(rows, key=lambda r: _parse_dt(r[CLOCK_COL]))
    vals: List[float | None] = [_to_float(r.get(IMPORT_COL)) for r in rows_sorted]

    deltas: List[float] = []
    for i in range(len(vals) - 1):
        v1, v2 = vals[i], vals[i + 1]
        if v1 is None or v2 is None:
            # skip broken pair
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


# ---------- Main ----------
def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    with INPUT_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    by_meter = _normalize_input(raw)

    # Build one array per meter (KEEP order stable by sorting meter ids)
    meter_ids = sorted(by_meter.keys(), key=lambda x: (len(x), x))
    per_meter: List[List[float]] = []
    for m in meter_ids:
        deltas = _compute_import_deltas(by_meter[m])
        # Even if empty, we'll pad later (all zeros)
        per_meter.append(deltas)

    # Left-pad to longest length using nearest-member extrapolation
    per_meter = _left_pad_nearest(per_meter)

    # Write pure array-of-arrays
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(per_meter, f, ensure_ascii=False, indent=2)

    # Optional: show quick summary
    n = len(per_meter)
    L = len(per_meter[0]) if n else 0
    print(f"✓ wrote {n} meter series to {OUTPUT_PATH} (uniform length = {L})")


if __name__ == "__main__":
    main()
