#!/usr/bin/env python3
"""print_data_vertical.py

Read a JSON file (supports regular JSON, newline-delimited JSON and large top-level arrays) and print its
contents vertically for easy inspection.

Usage:
  python print_data_vertical.py [path_to_json] [optional:key]

If a key is provided and the top-level object is a dict, the script will print values for that key.
"""
import json
import sys
from pathlib import Path


def print_vertical_from_obj(obj, indent=0):
    pad = '  ' * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"{pad}{k}:")
            print_vertical_from_obj(v, indent + 1)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            print(f"{pad}[{i}]")
            print_vertical_from_obj(item, indent + 1)
    else:
        print(f"{pad}{obj}")


def try_load_json(path: Path):
    with path.open('r', encoding='utf-8') as fh:
        return json.load(fh)


def try_ndjson(path: Path):
    """Try to parse the file as newline-delimited JSON (one JSON object per line)."""
    results = []
    with path.open('r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except Exception:
                # not ndjson
                return None
    return results


def stream_top_level_array(path: Path):
    """Simple streaming parser for a top-level JSON array of objects.

    This does not fully parse JSON robustly but handles common well-formed arrays containing objects.
    It yields Python dicts for each top-level element.
    """
    with path.open('r', encoding='utf-8') as fh:
        buf = ''
        in_array = False
        depth = 0
        for ch in fh.read():
            if not in_array:
                if ch == '[':
                    in_array = True
                continue
            # once in array, accumulate chars until we find balanced objects
            if ch == '{':
                depth += 1
            if depth > 0:
                buf += ch
            if ch == '}':
                depth -= 1
                if depth == 0:
                    # parse object
                    try:
                        yield json.loads(buf)
                    except Exception:
                        pass
                    buf = ''


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('data.json')
    key = sys.argv[2] if len(sys.argv) > 2 else None

    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(2)

    # Try normal load
    try:
        obj = try_load_json(path)
    except MemoryError:
        obj = None
    except Exception:
        obj = None

    if obj is not None:
        if key and isinstance(obj, dict) and key in obj:
            print_vertical_from_obj(obj[key])
        else:
            print_vertical_from_obj(obj)
        return

    # Try newline-delimited JSON
    nd = try_ndjson(path)
    if nd is not None:
        print_vertical_from_obj(nd)
        return

    # Try streaming a top-level array
    print("Falling back to streaming parse for large top-level array or other large format...")
    any_printed = False
    for i, item in enumerate(stream_top_level_array(path)):
        print(f"[{i}]")
        print_vertical_from_obj(item, indent=1)
        any_printed = True
        # limit output for usability
        if i >= 1000:
            print("...stopped after 1000 items")
            break

    if not any_printed:
        print("Unable to parse file with available strategies. Consider installing ijson for streaming JSON parsing or provide a smaller sample file.")


if __name__ == '__main__':
    main()
