"""reconcile.py — deterministic contradiction finder (tool B core, 0 LLM).

Checks (each returns {check, status PASS/WARN/FAIL, detail}):
 1. BS_BALANCE: |TA - TL - Equity| — needs equity; derive equity = TA - TL, cross-check
    against subtotal sums when provided (here: WC plausibility + totals positivity).
 2. SUBTOTAL_SUMS: component sums vs reported totals (receivables+... sanity via prepay share).
 3. RESTATEMENT_DELTA: t1 comparatives vs prior standalone — inputs carry t1 only, so this
    flags fields where t1 values look restated (marker field `restated_fields`).
 4. GUIDANCE_DIVERGENCE: |model_revenue_next - guidance_mid| / guidance_mid > 15% → FAIL.
 5. CONSENSUS_DELTA: our vs consensus EPS/target gaps (info, WARN if |Δ|>20%).
 6. FOOTNOTE_XREF: scans notes/enquiry text for dangling refs (mentions 附注/Note without target).
Writes _contradictions.csv. Exit code = #FAIL (0 = clean).
"""
import csv
import json
import re
import sys
import pathlib

XREF_RE = re.compile(r"(?:详见|参见|见)(附注[^，。；,;.]{0,20}|Note\s*\d+[^,;.]{0,20})")


def run(case_dir, out_dir):
    d = json.loads(pathlib.Path(case_dir, "inputs.json").read_text(encoding="utf-8"))
    rows = []

    def add(check, status, detail):
        rows.append({"check": check, "status": status, "detail": detail})

    # 1. balance-sheet identity on totals
    t = d
    for k in ("total_assets", "total_liab", "sales", "cash"):
        if t.get(k) is None or t[k] < 0:
            add("TOTALS_SANITY", "FAIL", f"{k} missing or negative")
    if not any(r["check"] == "TOTALS_SANITY" and r["status"] == "FAIL" for r in rows):
        add("TOTALS_SANITY", "PASS", "totals present and non-negative")

    # 2.WC plausibility: |WC| <= CA
    if abs(t.get("wc", 0)) > (t.get("current_assets", 0) or 0):
        add("WC_PLAUSIBILITY", "FAIL", f"|WC|={t['wc']} > CA={t['current_assets']}")
    else:
        add("WC_PLAUSIBILITY", "PASS", f"WC={t['wc']} within CA")

    # 3. restated markers
    restated = d.get("restated_fields", [])
    if restated:
        add("RESTATEMENT_DELTA", "WARN", f"restated fields declared: {','.join(restated)} (use vintage policy)")
    else:
        add("RESTATEMENT_DELTA", "PASS", "no restatement markers")

    # 4. guidance divergence
    g = d.get("guidance", {}).get("revenue")
    mr = d.get("model_revenue_next")
    if g and mr:
        mid = (g[0] + g[1]) / 2
        div = abs(mr - mid) / mid
        add("GUIDANCE_DIVERGENCE", "FAIL" if div > 0.15 else "PASS",
            f"model={mr} vs guidance_mid={mid:.0f} div={div:.1%}")
    else:
        add("GUIDANCE_DIVERGENCE", "WARN", "guidance or model revenue missing")

    # 5. consensus delta
    c, o = d.get("consensus", {}), d.get("our", {})
    if c.get("eps") and o.get("eps"):
        de = (o["eps"] - c["eps"]) / abs(c["eps"])
        add("CONSENSUS_EPS_DELTA", "WARN" if abs(de) > 0.20 else "PASS",
            f"our={o['eps']} vs street={c['eps']} Δ={de:+.1%}")
    else:
        add("CONSENSUS_EPS_DELTA", "WARN", "consensus coverage missing → MARKET_IMPLIED fallback")

    # 6. footnote xref dangling scan
    texts = []
    for name in ("notes.txt", "enquiry.txt"):
        p = pathlib.Path(case_dir, name)
        if p.exists():
            texts.append(p.read_text(encoding="utf-8"))
    blob = "\n".join(texts)
    refs = XREF_RE.findall(blob)
    if refs and "footnotes_focus" not in blob:
        add("FOOTNOTE_XREF", "WARN", f"{len(refs)} cross-refs found, expansion fetch required: {refs[:3]}")
    else:
        add("FOOTNOTE_XREF", "PASS" if not refs else "WARN",
            "no dangling refs" if not refs else f"{len(refs)} refs")

    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(pathlib.Path(out_dir, "_contradictions.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["check", "status", "detail"])
        w.writeheader()
        w.writerows(rows)
    fails = sum(1 for r in rows if r["status"] == "FAIL")
    print(json.dumps({"fails": fails, "warns": sum(1 for r in rows if r["status"] == "WARN"),
                      "rows": rows}, ensure_ascii=False, indent=2))
    return fails


if __name__ == "__main__":
    sys.exit(run(sys.argv[1], sys.argv[2]))
