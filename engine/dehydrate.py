"""dehydrate.py — enquiry boilerplate strip + footnote index + table-stitch check (0 LLM).

- Drops law-firm/accountant boilerplate lines (regex feature library), targets 15–20% retention.
- Builds _footnote_index.csv (note_id|title|pages|risk_score|source_class).
- Flags cross-page tables needing STITCH_WARN (long pipe-table runs).
Writes footnotes_focus/dehydrated.txt + _footnote_index.csv + dehydrate_log.csv.
"""
import csv
import json
import re
import sys
import pathlib

BOILERPLATE = re.compile(
    r"经核查认为|符合.*准则.*规定|具有合理性|在所有重大方面公允|in all material respects|特此说明")
RISK_KW = re.compile(r"担保|受限|质押|诉讼|关联方|VIE|表外|保理|contingen|guarantee|pledge|litigat|restrict")
XREF = re.compile(r"(?:详见|参见|见)(附注[^，。；,;.]{0,20}|Note\s*\d+)")


def run(case_dir, out_dir):
    src = pathlib.Path(case_dir, "enquiry.txt")
    text = src.read_text(encoding="utf-8") if src.exists() else ""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    dropped = [ln for ln in lines if BOILERPLATE.search(ln)]
    kept = [ln for ln in lines if not BOILERPLATE.search(ln)]
    retention = round(len(kept) / len(lines), 3) if lines else 0.0

    focus = pathlib.Path(out_dir, "footnotes_focus")
    focus.mkdir(parents=True, exist_ok=True)
    (focus / "dehydrated.txt").write_text("\n".join(kept), encoding="utf-8")

    risk_hits = sorted(set(RISK_KW.findall(text)))
    xrefs = XREF.findall(text)
    pipe_runs = sum(1 for ln in kept if ln.count("|") >= 4)
    index = [{"note_id": "ENQ-01", "title": "enquiry_reply_dehydrated",
              "pages": "raw/enquiry", "risk_score": 3 if risk_hits else 1,
              "risk_reason": ",".join(risk_hits[:6]) or "none",
              "source_class": "regulatory_enquiry",
              "expansion_from": ";".join(xrefs[:5])}]
    with open(pathlib.Path(out_dir, "_footnote_index.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(index[0].keys()))
        w.writeheader()
        w.writerows(index)
    with open(pathlib.Path(out_dir, "dehydrate_log.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lines_in", "lines_dropped", "lines_kept", "retention"])
        w.writeheader()
        w.writerow({"lines_in": len(lines), "lines_dropped": len(dropped),
                    "lines_kept": len(kept), "retention": retention})
    res = {"retention": retention, "risk_hits": risk_hits, "xrefs": xrefs,
           "stitch_warn": pipe_runs >= 3}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return res
