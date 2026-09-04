"""collect.py — deterministic source manifest builder (0 LLM, 0 network by default).

Given ticker/market/period, emits raw/_manifest.json listing every expected
document (filings + 24-month enquiries + latest transcript) with cache-first
resolution against workspace/shared_filing_cache/. No HTTP here: fetching is
a separate, rate-limited step; this script only plans + verifies cache hits.
"""
import json
import sys
import pathlib

def run(ticker, market, period, raw_dir, cache_dir="workspace/shared_filing_cache"):
    docs = [
        {"doctype": "AR", "name": f"{period}_{market}_AR.pdf", "class": "filing"},
        {"doctype": "ENQUIRY", "name": f"{period}_{market}_enquiry_reply.pdf", "class": "regulatory_enquiry"},
        {"doctype": "TRANSCRIPT", "name": f"{period}_{market}_transcript.pdf", "class": "transcript"},
    ]
    manifest = []
    for doc in docs:
        key = f"{market}/{doc['doctype']}/{ticker}/{period}"
        hit = (pathlib.Path(cache_dir) / key.replace("/", "_")).exists()
        manifest.append({**doc, "cache_key": key, "cache": "HIT" if hit else "MISS"})
    pathlib.Path(raw_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(raw_dir, "_manifest.json").write_text(
        json.dumps({"ticker": ticker, "market": market, "period": period,
                    "driver": "direct_scraper", "docs": manifest},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"cached": sum(1 for m in manifest if m["cache"] == "HIT"),
                      "total": len(manifest)}, ensure_ascii=False))
    return manifest
