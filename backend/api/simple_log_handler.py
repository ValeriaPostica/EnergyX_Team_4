from flask import request, jsonify
import os
import re
import shutil
import tempfile

# Resolve the simple_log path relative to this module (backend/api)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SIMPLE_LOG_PATH = os.path.join(DATA_DIR, "simple_log.txt")


def simple_log():
    """Append a human-readable line to backend/data/simple_log.txt.

    Expected JSON body: { "line": "..." }
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Require a single 'line' field (raw text to append)
        raw_line = json_data.get("line")
        if raw_line is None:
            return jsonify({"error": "Missing 'line' field (raw text to append)"}), 400

        # Ensure it ends with newline
        if not isinstance(raw_line, str):
            return jsonify({"error": "'line' must be a string"}), 400

        if not raw_line.endswith("\n"):
            raw_line = raw_line + "\n"

        # Helper: safely read lines from the existing file with fallbacks
        def safe_read_lines(path):
            if not os.path.exists(path):
                return []
            # try utf-8 first, then fall back with replacements
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return [l.rstrip("\n") for l in f]
            except Exception:
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        return [l.rstrip("\n") for l in f]
                except Exception:
                    # As last resort, read binary and decode replacing errors
                    try:
                        with open(path, "rb") as f:
                            data = f.read()
                        text = data.decode("utf-8", errors="replace")
                        return [l.rstrip("\n") for l in text.splitlines()]
                    except Exception:
                        return []

        # Read existing lines safely
        all_lines = safe_read_lines(SIMPLE_LOG_PATH)
        # Append the new incoming line (without trailing newline)
        all_lines.append(raw_line.rstrip("\n"))

        # Pattern: optional leading whitespace, digit 0-9, then ')' then content
        pattern = re.compile(r"^\s*([0-9]+)\)\s*(.*)$")
        base_indices = {"0", "1", "2", "3", "4"}
        latest: dict[str, str] = {key: "" for key in base_indices}

        # Walk through lines in order, update latest for matches
        for ln in all_lines:
            m = pattern.match(ln)
            if m:
                idx = m.group(1)
                base_indices.add(idx)
                latest[idx] = m.group(2)

        # Backup existing file before writing
        try:
            if os.path.exists(SIMPLE_LOG_PATH):
                shutil.copy2(SIMPLE_LOG_PATH, SIMPLE_LOG_PATH + ".bak")
        except Exception:
            # non-fatal: continue
            pass

        # Write atomically to avoid partial writes
        fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(SIMPLE_LOG_PATH))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
                for key in sorted(base_indices, key=lambda v: int(v)):
                    val = latest.get(key, "")
                    if val:
                        tmpf.write(f"{key}){val}\n")
                    else:
                        tmpf.write(f"{key})\n")
            # atomic replace
            os.replace(tmp_path, SIMPLE_LOG_PATH)
        finally:
            # ensure temp cleanup
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def simple_log_clear():
    """Truncate the simple_log file so it's empty. Intended to be called on user registration/login.

    This endpoint requires no body. It will return 200 on success.
    """
    try:
        # Ensure data dir exists
        os.makedirs(os.path.dirname(SIMPLE_LOG_PATH), exist_ok=True)
        # Truncate (clear) the file
        open(SIMPLE_LOG_PATH, "w", encoding="utf-8").close()
        return jsonify({"status": "cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
