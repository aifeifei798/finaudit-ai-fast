"""run_all.py — one-shot deterministic audit pipeline (tool A core, 0 LLM).

collect → dehydrate → metrics → reconcile → valuation → scenario → render → verdict
Usage: python3 engine/run_all.py --case engine/fixtures/SHADYCO_FY2024 --out workspace/targets/SHADYCO_FY2024 [--unresolved core_accounting]
Verdict: RED (do not touch) / YELLOW (watchlist only) / GREEN (investable).
"""
import argparse
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import collect
import dehydrate
import metrics
import reconcile
import valuation
import scenario

ap = argparse.ArgumentParser()
ap.add_argument("--case", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--unresolved", default=None)
args = ap.parse_args()
t0 = time.time()

case, out = args.case, args.out
d = json.loads(pathlib.Path(case, "inputs.json").read_text(encoding="utf-8"))
meta = d["meta"]
collect.run(meta["ticker"], meta["market"], meta["period"], f"{out}/raw")
dehydrate.run(case, f"{out}/extracted")
mres = metrics.run(case, f"{out}/extracted")
fails = reconcile.run(case, f"{out}/extracted")
vres = valuation.run(case, f"{out}/models", args.unresolved)
scenario.run(case, f"{out}/models")

reds = [f for f in mres["flags"]]
if fails > 0:
    reds.append("RECONCILE_FAIL")
tier = args.unresolved
if tier == "core_accounting":
    reds.append("UNRESOLVED_CORE")
pos_cap = 0.02 if tier == "core_accounting" else (0.03 if tier == "major_governance"
                                                 else (0.05 if tier else 0.10))
# execution gate
ex = d.get("execution", {})
adv_cap = 0.10 * ex.get("adv_30d", 0) / (ex.get("fund_size", 1) or 1)
pos_cap = round(min(pos_cap, adv_cap if adv_cap else pos_cap), 4)
short_ok = ex.get("borrow") not in ("none", "HTB") and ex.get("ctb", 0) <= 0.15

if reds:
    verdict, advice = "RED", "不能碰：有暴雷前兆，规避；有券也不做空" if not short_ok else "不能碰：规避，可做空对冲"
elif mres["m_verdict"] == "GREY" or tier:
    verdict, advice = "YELLOW", f"观察仓≤{pos_cap:.0%}，等季报验证"
else:
    verdict, advice = "GREEN", f"可研究，仓位≤{pos_cap:.0%}"

verdict_obj = {"ticker": meta["ticker"], "period": meta["period"], "verdict": verdict,
               "advice": advice, "red_flags": reds,
               "target": vres["target_listed"], "engine": vres["engine"],
               "position_cap": pos_cap, "short_allowed": short_ok,
               "elapsed_sec": round(time.time() - t0, 2)}
pathlib.Path(out).mkdir(parents=True, exist_ok=True)
pathlib.Path(out, "_verdict.json").write_text(
    json.dumps(verdict_obj, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(verdict_obj, ensure_ascii=False, indent=2))
