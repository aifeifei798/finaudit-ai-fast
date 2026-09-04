"""Deterministic Engine shared helpers (stdlib-first, 0 LLM, 0 network)."""
import csv
import json
import pathlib
import time

ENGINE_VERSION = "2.0.0"


def read_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def write_json(path, obj):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path, fieldnames, rows):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def timed(fn, *a, **k):
    t0 = time.time()
    out = fn(*a, **k)
    return out, round(time.time() - t0, 3)


def pct(a, b):
    if b in (0, None) or a is None or b is None:
        return None
    return (a - b) / abs(b)
