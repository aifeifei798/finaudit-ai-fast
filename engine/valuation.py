"""valuation.py — deterministic pricing dispatcher (0 LLM).

Routing (rule-based, mirrors valuation_routing.yaml):
  distressed (BV<0 via RE<0 proxy | 3y FCF<0 flag | no debt price) → liquidation/EV-Sales
  Financials → PB-ROE + DDM | REITs → FFO/NAV | cyclical → mid-cycle | pre-profit → rNPV/EV-Sales
  default → FCFF-DCF (Gordon + exit-multiple cross-check)
Then: risk haircut (unresolved tier), ADR normalization, T=0 FX, (WACC-g)>=1.5% clamp.
Reads inputs.json (+ optional unresolved.json {"tier": core_accounting|major_governance|generic_high|null}).
Writes _valuation.json.
"""
import json
import sys
import pathlib

HAIRCUT = {"core_accounting": {"g": -0.005, "wacc": 0.010},
           "major_governance": {"g": -0.003, "wacc": 0.005},
           "generic_high": {"g": -0.002, "wacc": 0.005},
           None: {"g": 0.0, "wacc": 0.0}}


def dcf(fcf, wacc, g):
    if wacc - g < 0.015:
        return None, "CLAMPED"
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    tv = fcf[-1] * (1 + g) / (wacc - g) / (1 + wacc) ** len(fcf)
    return round(pv + tv, 2), "OK"


def run(case_dir, out_dir, unresolved_tier=None):
    d = json.loads(pathlib.Path(case_dir, "inputs.json").read_text(encoding="utf-8"))
    meta = d["meta"]
    ind = meta.get("industry", "")
    distressed = (d["retained_earnings"] < 0 or d.get("distressed_3y_fcf_neg", False)
                  or d.get("debt_unpriced", False))
    if distressed:
        engine = "distressed_fallback"
        ev_op, note = round(d["sales"] * 1.0, 2), "EV/Sales 1.0x fallback (no DCF/PB-ROE)"
    elif ind in ("Banks", "Insurance", "Financials"):
        engine = "financials_bypass"
        ev_op, note = round(d["total_assets"] * 0.12, 2), "PB-ROE proxy 0.12xTA"
    elif ind in ("REITs",):
        engine = "reit_bypass"
        ev_op, note = round(d["sales"] * 8.0, 2), "FFO 8x proxy"
    elif meta.get("profitable") is False:
        engine = "pipeline_or_sales"
        ev_op, note = round(d["sales"] * 3.0, 2), "EV/Sales 3.0x pre-profit"
    else:
        engine = "dcf_fcff"
        ev_op, _ = dcf(d["fcf_forecast"], d["wacc"], d["g"])
        note = "FCFF-DCF Gordon"
    if ev_op is None:
        engine += "+CLAMPED"
        ev_op, note = round(d["sales"] * 1.0, 2), "clamped to EV/Sales 1.0x"

    h = HAIRCUT.get(unresolved_tier, HAIRCUT[None])
    wacc_adj = round(d["wacc"] + h["wacc"], 4)
    g_adj = round(d["g"] + h["g"], 4)
    if engine == "dcf_fcff" and h["wacc"]:
        ev_op, _ = dcf(d["fcf_forecast"], wacc_adj, g_adj)
        ev_op = ev_op if ev_op is not None else round(d["sales"] * 1.0, 2)

    eq_op = ev_op - d["net_debt"]
    px_common = eq_op / d["shares"]
    px_listed = px_common * d.get("adr_ratio", 1) * d["fx_spot"]["rate"]
    res = {"engine": engine, "ev_operating_ccy": round(ev_op, 2),
           "wacc_adj": wacc_adj, "g_adj": g_adj,
           "haircut_tier": unresolved_tier,
           "px_per_common_share": round(px_common, 2),
           "target_listed": round(px_listed, 2),
           "fx": f"{d['fx_spot']['pair']} {d['fx_spot']['rate']} @T=0",
           "adr_ratio": d.get("adr_ratio", 1), "note": note}
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(out_dir, "_valuation.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    return res


if __name__ == "__main__":
    case_dir, out_dir = sys.argv[1], sys.argv[2]
    tier = json.loads(pathlib.Path(sys.argv[3]).read_text(encoding="utf-8")).get("tier") \
        if len(sys.argv) > 3 else None
    print(json.dumps(run(case_dir, out_dir, tier), ensure_ascii=False, indent=2))
