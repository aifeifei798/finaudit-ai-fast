# FinAudit AI Fast

Fraud screening in seconds, not hours. Math runs as code (zero tokens); only judgment uses LLMs — 3 agents, 3 tools.

## Why Fast exists

The classic 19-agent full loop answers everything and ships nothing on time. Fast answers three questions only:

1. **Can we touch this ticker?** (`audit` — RED / YELLOW / GREEN in ~30 seconds)
2. **Do the statements contradict themselves?** (`reconcile` — pure code, zero LLM)
3. **What did the market miss?** (`delta` — 3 consensus-vs-guidance moves + conviction)

If the goal is dodging a billion-dollar blowup or catching a mispriced Alpha, lightness beats completeness.

## Architecture

| Layer | Members | Cost |
|---|---|---|
| Deterministic Engine (`engine/`) | `collect / dehydrate / metrics / reconcile / valuation / scenario / render / run_all` | 0 tokens, seconds |
| Agent 1 — Forensic Auditor | dehydrated enquiry replies + footnote cross-refs + call-transcript drift + PII-sanitized flows; finds contradictions, scores suspicions | 1 focused call |
| Agent 2 — Business Strategist | moat / growth / guidance / Consensus gap; states where the Alpha is | 1 focused call |
| Agent 3 — Magistrate (default) | verdict / haircut / position; dismisses evidence-free charges; sole sign-off | 1 ruling call |

The legacy 19-agent loop is preserved read-only under `.opencode/{agents,commands}/_legacy/`.

## Tools

| Command | What it does | Latency |
|---|---|---|
| `audit --ticker=XXX` | Engine verdict first, auditor qualitative pass, magistrate one-page ruling. One question only: touchable or not? | ~30s |
| `reconcile --ticker=XXX` | Cross-checks statements vs notes (`_contradictions.csv`). FAIL opens a case; all-PASS returns "books balance". | seconds, 0 LLM |
| `delta --ticker=XXX` | Guidance vs Consensus radar. 3 market-missed moves + conviction; euphoria (>20% above street) blocks heavy positions. | 1 call |

## Quickstart

```bash
pip install -r engine/requirements.txt
python3 engine/run_all.py --case engine/fixtures/SHADYCO_FY2024 --out workspace/targets/SHADYCO_FY2024
# verdict: RED — do not touch (5 flags, short blocked), 0.0s, 0 tokens

python3 engine/reconcile.py engine/fixtures/CLEANCO_FY2024 workspace/targets/CLEANCO_FY2024/extracted
# fails: 0 — books balance
```

Add a case by copying `engine/fixtures/CLEANCO_FY2024/` and editing `inputs.json` (single numeric contract).

## Engine contract

- **In**: `engine/fixtures/<TICKER_PERIOD>/inputs.json` (statements + guidance + consensus + credit + execution), optional text (`notes/enquiry/transcript.txt`) and `flows.csv`.
- **Out**: sandbox `workspace/targets/<TICKER_PERIOD>/` — `_verdict.json`, `_fraud_metrics.json`, `_contradictions.csv`, `_valuation.json`, `_sensitivity.csv`, `Valuation_Model.xlsx`, `tagged_flows.csv`.
- **Rules baked in**: Python-first numbers; no FCFF-DCF for financials/REITs/pre-profit; distressed fallback; beginning-debt interest (never circular); T=0 spot FX; borrow/CTB gate; PII never leaves the box.

## Guardrails

1. Agents never recompute engine numbers — violations are sent back.
2. Every final number needs FN/Calc/lineage; evidence-free charges are dismissed by the magistrate.
3. Raw PII never enters any LLM (salted local sanitizer, vault destroyed after use).
4. No ADV/CTB data, no position; `CREDIT_DISTRESS` caps at watchlist.

## Repo map

- `engine/` — deterministic layer + fixtures + `requirements.txt`
- `.opencode/agents/` — `magistrate.md`, `forensic-auditor.md`, `business-strategist.md` (+ `_legacy/`)
- `.opencode/commands/` — `audit`, `reconcile`, `delta` (`.json` + `.md` each) (+ `_legacy/`)
- `.opencode/skills/` — 21 method manuals (kept, agents read them but never reinvent them)
- `workspace/params/` — market tables, routing, penalty matrix, ingestion drivers
- `eval/` — 50-case Golden regression suite (Recall ≥92% / FalseAlarm ≤8%)

## License

Proprietary - For internal financial audit use only.
