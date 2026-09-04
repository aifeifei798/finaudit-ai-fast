"""metrics.py — deterministic fraud tripwires (0 LLM). Reads inputs.json, writes _fraud_metrics.json.

Covers: Beneish M-Score (1999 coeffs), Altman Z, Sloan accruals,
cash-debt paradox (Kangmei trigger), triangular probes (v1.7),
treasury-pool tagger (v1.6 Step0b), credit-distress flag (v1.8).
"""
import csv
import json
import re
import sys
import pathlib

TREASURY_MEMO = re.compile(r"内部归集|资金下拨|集中收付|sweep|pooling|cash concentration", re.I)


def m_score(t, t1):
    def safe_div(a, b):
        return a / b if b else None
    dsri = safe_div(t["receivables"] / t["sales"], t1["receivables"] / t1["sales"])
    gmi = safe_div((t1["sales"] - t1["cogs"]) / t1["sales"], (t["sales"] - t["cogs"]) / t["sales"])
    aqi = safe_div(1 - (t["current_assets"] + t["ppe_net"]) / t["total_assets"],
                   1 - (t1["current_assets"] + t1["ppe_net"]) / t1["total_assets"])
    sgi = safe_div(t["sales"], t1["sales"])
    lvgi = safe_div(t["total_liab"] / t["total_assets"], t1["total_liab"] / t1["total_assets"])
    depi = safe_div(t1["depreciation"] / (t1["depreciation"] + t1["ppe_net"]),
                    t["depreciation"] / (t["depreciation"] + t["ppe_net"]))
    sgai = safe_div(t["sga"] / t["sales"], t1["sga"] / t1["sales"])
    tata = (t["income_before_extra"] - t["cfo"]) / t["total_assets"]
    parts = {"DSRI": dsri, "GMI": gmi, "AQI": aqi, "SGI": sgi, "LVGI": lvgi,
             "DEPI": depi, "SGAI": sgai, "TATA": tata}
    if any(v is None for v in parts.values()):
        return None, parts
    m = (-4.87 + 0.920 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi
         + 0.115 * lvgi - 0.172 * sgai + 4.679 * tata - 0.327 * depi)
    return round(m, 3), {k: round(v, 4) for k, v in parts.items()}


def z_score(t):
    ta = t["total_assets"]
    z = (1.2 * t["wc"] / ta + 1.4 * t["retained_earnings"] / ta
         + 3.3 * t["ebit"] / ta + 0.6 * t["mve"] / t["total_liab"]
         + 1.0 * t["sales"] / ta)
    return round(z, 3)


def cash_debt_paradox(t):
    hits = []
    if t["cash"] / (t["short_debt"] or 1) > 1.5:
        hits.append("cash_to_shortdebt>1.5")
    if t["interest_expense"] / (t["cash"] or 1) > 0.05:
        hits.append("interest_over_cash>5%")
    return hits


def triangular_probes(d):
    """Flow-statement triangle (v1.7): catches off-BS factoring even when flows look clean."""
    t, t1 = d, d["t1"]
    flags = []
    if t["cash"] / (t["short_debt"] or 1) > 1.5 and t["short_debt"] > 0.2 * t["total_assets"]:
        flags.append("BIG_SAVE_BIG_BORROW")
    prepay_g = (t["prepay"] - t1["prepay"]) / (t1["prepay"] or 1)
    sales_g = (t["sales"] - t1["sales"]) / (t1["sales"] or 1)
    if prepay_g - sales_g > 0.20 or t["prepay"] / t["total_assets"] > 0.10:
        flags.append("PREPAY_SURGE")
    if abs((t["cfo"] / (t["sales"] or 1)) - 0.10) > 0.30:
        flags.append("FLOW_SCALE_DIVERGENCE")
    return {"prepay_growth": round(prepay_g, 3), "sales_growth": round(sales_g, 3), "flags": flags}


def tag_treasury_flows(flows_path):
    """Step0b fingerprint: memo + timing + offset. Returns (tagged_rows, treasury_count, suspicious)."""
    rows = list(csv.DictReader(open(flows_path, encoding="utf-8-sig")))
    memos = [r.get("memo", "") for r in rows]
    treasury_n = sum(1 for m in memos if TREASURY_MEMO.search(m or ""))
    # offsetting-pair heuristic: same amount up then down between same parties
    pairs = 0
    seen = {}
    for r in rows:
        try:
            amt = float(r.get("amount", 0))
        except ValueError:
            continue
        key = (round(amt, 2), r.get("payer"), r.get("payee"))
        rev = (round(amt, 2), r.get("payee"), r.get("payer"))
        if rev in seen:
            pairs += 1
        seen[key] = True
    out = []
    for r in rows:
        r2 = dict(r)
        r2["tag"] = "TREASURY_POOL" if TREASURY_MEMO.search(r.get("memo", "") or "") else ""
        out.append(r2)
    return out, treasury_n, pairs


def run(case_dir, out_dir):
    d = json.loads(pathlib.Path(case_dir, "inputs.json").read_text(encoding="utf-8"))
    m, parts = m_score(d, d["t1"])
    z = z_score(d)
    sloan = round((d["net_income"] - d["cfo"]) / d["total_assets"], 4)
    paradox = cash_debt_paradox(d)
    tri = triangular_probes(d)
    verdict_flags = []
    if m is not None and m > -1.78:
        verdict_flags.append("M_SCORE_RED")
    elif m is not None and m > -2.22:
        verdict_flags.append("M_SCORE_GREY")
    if len(paradox) >= 2:
        verdict_flags.append("CASH_DEBT_PARADOX")
    if tri["flags"]:
        verdict_flags.append("TRIANGULAR_" + tri["flags"][0])
    credit_bps = d.get("credit", {}).get("spread_bps")
    if credit_bps is not None and credit_bps > 800:
        verdict_flags.append("CREDIT_DISTRESS")

    flows_path = pathlib.Path(case_dir, "flows.csv")
    treasury = {}
    if flows_path.exists():
        tagged, tn, pairs = tag_treasury_flows(str(flows_path))
        treasury = {"rows": len(tagged), "treasury_tagged": tn, "offset_pairs": pairs}
        with open(pathlib.Path(out_dir, "tagged_flows.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(tagged[0].keys()))
            w.writeheader()
            w.writerows(tagged)

    res = {"m_score": m, "m_parts": parts, "m_verdict": ("RED" if m is not None and m > -1.78
          else "GREY" if m is not None and m > -2.22 else ("N/A" if m is None else "PASS")),
           "z_score": z, "sloan": sloan, "cash_debt_hits": paradox,
           "triangular": tri, "credit_spread_bps": credit_bps,
           "treasury": treasury, "flags": verdict_flags}
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(out_dir, "_fraud_metrics.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    return res


if __name__ == "__main__":
    case_dir, out_dir = sys.argv[1], sys.argv[2]
    print(json.dumps(run(case_dir, out_dir), ensure_ascii=False, indent=2))
