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
- `workspace/peer_benchmarks/` — industry peer library + SW/HS/GICS mapping
- `workspace/targets/_TEMPLATE/` — target sandbox canonical layout + `pipeline-state.json`
- `workspace/reviews/` — pre-valuation sign-off template + challenge log
- `eval/` — 50-case Golden regression suite (Recall ≥92% / FalseAlarm ≤8%)

## 功能清单（全功能）

### 1. 三把小刀（`.opencode/commands/`）
- `audit --ticker=XXX`：秒级排雷。`run_all.py` 先行（RED/YELLOW/GREEN + `red_flags` + 目标价 + 仓位帽），`forensic-auditor` 定性复核，`magistrate` 一页裁决。只答：能不能碰 / 有无暴雷前兆。
- `reconcile --ticker=XXX`：极速对账，纯 `reconcile.py`，0 LLM。输出 `_contradictions.csv`，FAIL 立案，WARN 观察，全 PASS 回“账平”。
- `delta --ticker=XXX`：预期差雷达。`business-strategist` 输出 3 条市场没反应的核心变动（指引/Consensus 原文 + Δ% + 方向），`magistrate` 定 conviction；无覆盖写 N/A，高亢奋（内在价值低于 Consensus 超 20%）禁重仓。

### 2. 确定性 Engine（`engine/`，0 LLM，0 网络）
- `collect.py`：采集清单，按 ticker/market/period 生成 `raw/_manifest.json`（AR + 问询函 + 电话会，cache-first）。
- `dehydrate.py`：问询函脱水，去套话（目标留存 15–20%），输出 `footnotes_focus/dehydrated.txt` + `_footnote_index.csv` + `dehydrate_log.csv`，附风险关键词与跨页表 STITCH_WARN。
- `metrics.py`：定量排雷，Beneish M-Score + Altman Z + Sloan 应计 + 存贷双高悖论 + 三角探针（BIG_SAVE_BIG_BORROW / PREPAY_SURGE / FLOW_SCALE）+ 资金池指纹 + 信用困境（spread > 800bps），输出 `_fraud_metrics.json` + `tagged_flows.csv`。
- `reconcile.py`：6 项对账（总额 sanity / WC 合理性 / 重述标记 / 指引偏离>15% FAIL / Consensus 缺口>20% WARN / 附注悬空引用），输出 `_contradictions.csv`，exit code = FAIL 数。
- `valuation.py`：Dispatcher 定价。困境走清算/EV-Sales 兜底；金融走 PB-ROE+DDM；REITs 走 FFO/NAV；周期走中周期；未盈利走 rNPV/EV-Sales；默认 FCFF-DCF（Gordon + exit 双检，WACC-g ≥ 1.5% 熔断），叠加 unresolved 折价、ADR/T=0 汇率，输出 `_valuation.json`。
- `scenario.py`：Bull/Base/Bear（0.8x/1x/1.2x）+ WACC×g 网格，输出 `_sensitivity.csv`。
- `render.py`：活表构建，openpyxl 生成 `Valuation_Model.xlsx`（Assumptions/Calc/Summary 全公式，利息按期初债务防循环）+ `excel_verify.log`。
- `run_all.py`：一键全链 collect→render→`_verdict.json`（RED/YELLOW/GREEN + advice + `position_cap` + `short_allowed` + ADV/CTB 执行门 + 借券门禁）。

### 3. 三个 Agent（`opencode.json`，default=`magistrate`）
- `magistrate (primary)`：唯一签收人，综合 Engine + 双 subagent，拍板结论/折价率/仓位，无证据指控直接 Dismiss。
- `forensic-auditor (subagent)`：定性排雷，只找矛盾打分（疑点|证据|违背|severity|penalty_tier），不做算术。
- `business-strategist (subagent)`：只答 Alpha 在哪（护城河/增速/指引/Consensus 分歧 + conviction），不做算术。

### 4. 21 Skills（方法手册，只读调用）
排雷类：`quantitative-fraud-metrics`、`governance-redflags-skill`、`black-account-checker`、`pii-sanitizer-skill`、`esg-redflag-skill`、`sentiment-event-skill`；估值类：`valuation-modeling-skill`、`peer-comparison-skill`、`consensus-benchmarker-skill`、`macro-context-skill`、`portfolio-construction-skill`；工程类：`financial-parser-skill`、`financial-research-skill`、`multi-doc-reasoning-skill`、`market-adapter-skill`、`evidence-locker-skill`、`citation-engine-skill`、`professional-reporting-skill`、`adversarial-skeptic-skill`、`excel-export-skill`、`chart-visualization-skill`。

### 5. 参数与模板（`workspace/`）
- `params/cn|hk|us.yaml`：分市场准则/货币/FX 来源/WACC-g 边界/质押担保阈值/CTB 阻断/欺诈词库。
- `params/valuation_routing.yaml`：估值路由 + SOTP + SBC/租赁规则。
- `params/risk_penalty_matrix.yaml`：core/major/generic 三档 → g/WACC 惩罚 + 2%/3%/5% 仓位硬顶。
- `params/ingestion.yaml`：IAL 摄取契约（direct_scraper / institutional_terminal）。
- `peer_benchmarks/` + `targets/_TEMPLATE/` + `reviews/`：可比公司库、沙盒标准目录（含 `_bibliography.csv` / `_reconciliation_log.csv` / `pipeline-state.json`）、投前签收与 Challenge Log 模板。

### 6. Fixtures 与回归
- `engine/fixtures/CLEANCO_FY2024`（GREEN）/ `SHADYCO_FY2024`（RED + flows/enquiry）：`inputs.json` 为唯一数字契约，加新案复制即得。
- `eval/golden_benchmark.yaml + run_eval.py`：50 案金标准（25 fraud + 25 clean），门禁 Recall ≥ 0.92 / FalseAlarm ≤ 0.08。

### 7. 归档（只读备查）
- `.opencode/agents/_legacy/`：v1.x 19-Agent 全闭环归档。
- `.opencode/commands/_legacy/`：`report/screen/dcf/qa/black-account` 旧命令归档。

## License

Proprietary - For internal financial audit use only.
