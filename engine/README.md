# Engine — Deterministic Layer (v2.0, 0 LLM, 0 network)

Pure-code pipeline. Accounting is accounting; formulas are formulas. Seconds, zero tokens.

## Scripts
| Script | In | Out |
|---|---|---|
| `collect.py` | ticker/market/period | `raw/_manifest.json` (cache-first plan) |
| `dehydrate.py` | enquiry.txt | `footnotes_focus/dehydrated.txt`, `_footnote_index.csv`, `dehydrate_log.csv` |
| `metrics.py` | inputs.json (+flows.csv) | `_fraud_metrics.json`, `tagged_flows.csv` |
| `reconcile.py` | inputs.json (+notes/enquiry.txt) | `_contradictions.csv` (exit code = #FAIL) |
| `valuation.py` | inputs.json (+unresolved tier) | `_valuation.json` |
| `scenario.py` | inputs.json | `_sensitivity.csv` |
| `render.py` | inputs.json | `Valuation_Model.xlsx` + `excel_verify.log` |
| `run_all.py` | case dir | full chain + `_verdict.json` (RED/YELLOW/GREEN) |

## Run
```bash
pip install -r engine/requirements.txt
python3 engine/run_all.py --case engine/fixtures/SHADYCO_FY2024 --out workspace/targets/SHADYCO_FY2024
python3 engine/reconcile.py engine/fixtures/CLEANCO_FY2024 workspace/targets/CLEANCO_FY2024/extracted
```

## Fixtures
`engine/fixtures/{CLEANCO,SHADYCO}_FY2024/` — one clean (GREEN), one fraudulent (RED).
`inputs.json` is the single numeric contract; add a case by copying a fixture.
