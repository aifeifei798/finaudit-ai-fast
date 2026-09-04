"""scenario.py — Bull/Base/Bear + WACC×g grid (0 LLM). Writes _sensitivity.csv."""
import csv
import json
import sys
import pathlib
from valuation import dcf


def run(case_dir, out_dir):
    d = json.loads(pathlib.Path(case_dir, "inputs.json").read_text(encoding="utf-8"))
    base = d["fcf_forecast"]
    sc = {"Bear": [x * 0.8 for x in base], "Base": base, "Bull": [x * 1.2 for x in base]}
    rows = []
    for name, fcf in sc.items():
        ev, flag = dcf(fcf, d["wacc"], d["g"])
        rows.append({"scenario": name, "ev": ev if ev else "N/A (clamped)", "flag": flag})
    for dw in (-0.01, 0.0, 0.01):
        for dg in (-0.005, 0.0, 0.005):
            ev, flag = dcf(base, d["wacc"] + dw, d["g"] + dg)
            rows.append({"scenario": f"WACC{dw:+.0%}_g{dg:+.1%}",
                         "ev": ev if ev else "N/A (clamped)", "flag": flag})
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(pathlib.Path(out_dir, "_sensitivity.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["scenario", "ev", "flag"])
        w.writeheader()
        w.writerows(rows)
    return rows


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1], sys.argv[2]), ensure_ascii=False, indent=2))
