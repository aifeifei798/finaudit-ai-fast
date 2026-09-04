# FinAudit AI Fast (v2.0)

> **Fraud screening in seconds, not hours.**  
> Math runs as deterministic code (zero tokens). Only judgment uses LLMs.  
> **3 commands. 3 agents. Zero agent cosplay.**

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Latency: ~30s](https://img.shields.io/badge/Screening%20Latency-~30s-green.svg)](#tools)
[![Eval: Recall ≥ 92%](https://img.shields.io/badge/Eval%20Recall-%E2%89%A592%25-brightgreen.svg)](#eval--golden-benchmark)

---

## ⚡ The Manifesto: Death to "Agent Cosplay"

The legacy 19-agent autonomous loop was an academic masterpiece and an operational disaster. It answered every theoretical question, consumed millions of tokens, ran for 30 minutes, hallucinated balance sheet arithmetic, and delivered reports long after the market closed.

**In fundamental equity research, lightness beats completeness.** A buy-side portfolio manager before market open does not need an 80-page hallucinated essay. They need precise answers to **three questions only**:

1. **Can we touch this ticker?** (`audit` → **RED / YELLOW / GREEN** in ~30 seconds)
2. **Do the statements contradict themselves?** (`reconcile` → Pure code, **0 LLM**, instant diff)
3. **What did the market miss?** (`delta` → Guidance vs. Consensus divergence in 1 call)

**FinAudit AI Fast** enforces a strict architectural boundary:
* **The Deterministic Engine (`engine/`)** runs 100% of accounting, ratios, forensic metrics, and valuation models in compiled Python. **Cost: $0.00. Tokens: 0. Latency: Milliseconds.**
* **The 3 Focused Agents** are strictly prohibited from calculating numbers. They act exclusively as non-structured text litigators and decision judges.

---

## 🏛️ Architecture: The Two-Tier Paradigm

```
┌────────────────────────────────────────────────────────────────────────┐
│                      INPUTS CONTRACT (inputs.json)                     │
│    Statements + Footnotes + 24M Enquiry Letters + Earnings Calls + CTB │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────▼────────────────────────────────┐
    │          TIER 0: DETERMINISTIC ENGINE (engine/*.py)            │
    │  • 0 Tokens • 0 LLM • 100% Deterministic • Sub-Second Math     │
    │  ------------------------------------------------------------  │
    │  [collect] ──► [dehydrate] ──► [metrics] ──► [reconcile]       │
    │                                    │                           │
    │  [render]  ◄── [scenario]  ◄── [valuation] ◄── [run_all]       │
    └───────────────────────────────┬────────────────────────────────┘
                                    │ Generates canonical artifacts:
                                    │ _fraud_metrics, _contradictions,
                                    │ _valuation, _sensitivity, model.xlsx
                                    ▼
    ┌────────────────────────────────────────────────────────────────┐
    │               TIER 1 & 2: AGENTIC JUDGMENT (LLM)               │
    │  • Exactly 3 Focused Roles • Strict Evidentiary Standards      │
    │  ------------------------------------------------------------  │
    │                                                                │
    │   [Agent 1: Forensic Auditor]      [Agent 2: Business Strategist]
    │   (Scans dehydrated text,          (Extracts moat, guidance gap,
    │    tone drift & sanitized flows)    and Consensus divergence)   │
    │               │                                │               │
    │               └────────────────┬───────────────┘               │
    │                                ▼                               │
    │                   [Agent 3: The Magistrate]                    │
    │                   (Sole sign-off, dismisses                    │
    │                    evidence-free noise, sets                   │
    │                    haircuts & position caps)                   │
    └────────────────────────────────┬───────────────────────────────┘
                                     │
                                     ▼
                   FINAL VERDICT & ACTIONABLE POSITION
               [RED / YELLOW / GREEN] + Max Allocation %
```

---

## 🛠️ The Three Precision Knives

| Command | Operational Question | Engine Layer | LLM Calls | Typical Latency |
|---|---|---|---|---|
| `audit --ticker=XXX` | **"Is this investable or an explosive landmine?"** | `run_all.py` | 2 calls (`auditor` + `magistrate`) | **~30s** |
| `reconcile --ticker=XXX` | **"Do the financial statements contradict the notes?"** | `reconcile.py` | **0 calls** (Pure Code) | **< 1s** |
| `delta --ticker=XXX` | **"Where is our variant perception vs. the Street?"** | `valuation.py` | 1 call (`strategist`) | **~5s** |

### 1. `reconcile --ticker=XXX` (Zero-Token Forensic Diff)
Runs 6 automated reconciliation checks across financial tables and footnotes:
* Mathematical sanity across balance sheet, income, and cash flow statements.
* Working capital change consistency vs. cash flow items.
* As-reported vs. as-restated historical retrofits.
* Official management guidance deviation > 15% (**FAIL**).
* Street consensus divergence > 20% (**WARN**).
* Dangling footnote cross-references (`STITCH_WARN`).
* **Output:** `_contradictions.csv` (Exit code = count of hard failures).

### 2. `audit --ticker=XXX` (Flash Gatekeeper)
Executes a multi-tier forensic interrogation:
1. `run_all.py` executes quantitative forensics and valuation routing.
2. `forensic-auditor` evaluates dehydrated enquiry replies (15–20% retention), footnote disclosures, and salted bank flows.
3. `magistrate` holds a dialectical hearing:
   * **Dismiss without Merit**: Automatically strikes down speculative or evidence-free allegations made by red-team prompts.
   * **Penalty Matrix**: Binds verified accounting issues to strict WACC/terminal growth ($g$) haircuts and position hard caps (2%, 3%, or 5%).
* **Output:** `_verdict.json` + one-page executive ruling (`_audit_flash.md`).

### 3. `delta --ticker=XXX` (Variant Perception Radar)
Uncovers market alpha by isolating the delta between consensus whisper numbers and management guidance:
* Compares latest management call transcript guidance with Bloomberg/FactSet/Wind consensus datasets.
* Synthesizes the **Top 3 Structural Divergences** (verbatim citation, $\Delta\%$, directional conviction).
* **Euphoria Lockout**: If market consensus exceeds intrinsic DCF/Earnings power by >20%, heavy long positions are strictly vetoed.

---

## ⚙️ Deterministic Engine (`engine/`)

The engine is built in Python (`numpy`, `pandas`, `openpyxl`). It contains **zero network calls, zero LLM dependencies, and zero nondeterminism**:

* **`collect.py`**: Manages the canonical triple-asset collection (`_manifest.json`): Periodic Filings (AR/10-K), 24-Month Regulatory Enquiry Letters, and Q&A Earnings Call Transcripts. Utilizes a shared persistent filing cache.
* **`dehydrate.py`**: Strips out legal disclaimers, boilerplate auditor text, and regulatory recitations. Compresses 100-page enquiry replies down to 15–20% critical density while stitching cross-page table fragments.
* **`metrics.py`**: Computes quantitative forensic batteries:
  * **Beneish M-Score**, **Altman Z-Score**, and **Sloan Accruals**.
  * **Kangmei Paradox Trigger**: Detects anomalous concurrent spikes in high liquid cash and high short-term interest-bearing debt.
  * **Triangular Factoring Matrix**: Identifies off-balance-sheet disguised factoring and anomalous equipment prepayments.
  * **Treasury Pool Fingerprint**: Cleanses internal bank sweep/pooling false alarms via timestamp & offsetting heuristics.
  * **Credit Spread Sentinel**: Detects debt market distress (spreads > 800 bps).
* **`valuation.py`**: Dynamic Valuation Dispatcher:
  * Distressed entities ($BV < 0$ or FCF $< 0$) $\to$ Liquidation / EV-Sales fallback.
  * Financials (Banks/Insurance) $\to$ PB-ROE / DDM.
  * Real Estate / REITs $\to$ FFO / NAV.
  * Standard Corporates $\to$ Normalized FCFF-DCF with $T=0$ Spot FX iron law, ADR ratio normalization, and Gordon growth clamp ($(WACC - g) \ge 1.5\%$).
* **`render.py`**: Generates a fully dynamic, audit-ready `Valuation_Model.xlsx`. Uses **Beginning-Debt Interest Balancing** to mathematically eradicate circular calculation loops while preserving dynamic cell linking.

---

## 🛡️ Non-Negotiable Financial Guardrails

1. **Arithmetic Invariant**: LLM agents are strictly forbidden from modifying or recomputing any numeric metric generated by `engine/`. Violations are immediately aborted.
2. **Execution Reality Check**: If 30-day Average Daily Volume (ADV) or Cost to Borrow (CTB) data is missing, **the system refuses to generate target share allocations**. Short recommendations are hard-blocked if CTB $> 15\%$ or borrow is unavailable.
3. **Credit Dominance**: If corporate bond yields or CDS spreads exceed **800 bps (`CREDIT_DISTRESS`)**, any equity buy recommendation is vetoed, and the ticker is locked into a liquidation/watchlist cap.
4. **Epistemic Hygiene**: Every qualitative charge leveled by the `forensic-auditor` must cite an explicit footnote, enquiry line, or cash reconciliation delta. The `magistrate` dismisses unquantified rhetoric with prejudice.
5. **PII Isolation**: Bank transactions pass through local HMAC-salted deterministic pseudonymization. The mapping vault is destroyed in memory immediately post-run. Raw PII never hits an API.

---

## 🚀 Quickstart

### 1. Installation
```bash
git clone https://github.com/your-org/finaudit-ai-fast.git
cd finaudit-ai-fast
pip install -r engine/requirements.txt
```

### 2. Run Deterministic Baseline (< 1 Second)
```bash
# Execute full engine pipeline on a high-risk fraudulent case
python3 engine/run_all.py \
  --case engine/fixtures/SHADYCO_FY2024 \
  --out workspace/targets/SHADYCO_FY2024

# Output:
# [ENGINE] Processing SHADYCO_FY2024...
# [METRICS] Kangmei Paradox: TRIGGERED (Cash: $4.2B, ST-Debt: $4.1B)
# [CREDIT] Credit spread 920bps > 800bps -> CREDIT_DISTRESS active
# [VERDICT] RED — DO NOT TOUCH (5 flags, short blocked by CTB=45%)
# Execution time: 0.28s | Tokens consumed: 0
```

### 3. Run Instant Statement Reconcile (0 Tokens)
```bash
python3 engine/reconcile.py \
  engine/fixtures/CLEANCO_FY2024 \
  workspace/targets/CLEANCO_FY2024/extracted

# Output:
# [RECONCILE] Scanning statements against notes...
# [CHECK 1] Balance Sheet Net Asset Sanity: PASS
# [CHECK 2] Working Capital Delta vs Cash Flow: PASS
# [CHECK 3] Guidance Discrepancy <= 15%: PASS
# Result: 0 failures — Books balance perfectly.
```

### 4. Run Agentic Gatekeeper (`audit`)
```bash
# Run through opencode / CLI wrapper
audit --ticker=SHADYCO_FY2024
# Triggers: run_all.py -> forensic-auditor -> magistrate ruling (~30s)
```

---

## 📊 Eval & Golden Benchmark

To prevent silent performance degradation caused by upstream LLM API updates, FinAudit Fast maintains an automated regression suite in `eval/`:

```bash
python3 eval/run_eval.py
```

* **Dataset**: 50 historic financial reporting cycles.
  * **25 Confirmed Historic Frauds**: Enron, Luckin Coffee, Wirecard, Kangmei Pharmaceutical, Evergrande, etc.
  * **25 Pristine Blue-Chips**: Apple, Microsoft, Kweichow Moutai, TSMC, Yangtze Power, etc.
* **Production Gate Criteria**:
  $$\text{Fraud Recall} \ge 92.0\% \quad \Big| \quad \text{False Alarm Rate (Type I Error)} \le 8.0\%$$

---

## 📂 Repository Map

```
finaudit-ai-fast/
├── engine/                          # Deterministic Layer (0 Tokens)
│   ├── collect.py                   # Filing/Enquiry/Transcript ingestor
│   ├── dehydrate.py                 # Legal boilerplate de-hydrator (15-20%)
│   ├── metrics.py                   # M-Score, Z-Score, Sloan, Triangular checks
│   ├── reconcile.py                 # Statement-to-note consistency checks
│   ├── valuation.py                 # Multi-engine valuation dispatcher
│   ├── scenario.py                  # WACC x g scenario matrix
│   ├── render.py                    # Non-circular dynamic Excel generator
│   ├── run_all.py                   # Master deterministic orchestrator
│   └── fixtures/                    # Test cases (CLEANCO, SHADYCO)
├── .opencode/
│   ├── agents/                      # Active minimal agent triumvirate
│   │   ├── magistrate.md            # Primary: Ruling, dismissal, position caps
│   │   ├── forensic-auditor.md      # Subagent: Qualitative contradictions
│   │   ├── business-strategist.md   # Subagent: Moat, guidance & consensus
│   │   └── _legacy/                 # Archived v1.x 19-agent framework
│   ├── commands/                    # User entry points: audit, reconcile, delta
│   └── skills/                      # 21 reference method manuals
├── workspace/
│   ├── params/                      # Market params (cn/hk/us.yaml, risk_penalty)
│   ├── peer_benchmarks/             # Industry benchmark database
│   └── targets/                     # Isolated per-ticker execution sandboxes
└── eval/                            # 50-case Golden Benchmark harness
```

---

## ⚖️ License

**Proprietary Commercial Architecture.**  
Authorized for internal quantitative research, hedge fund due diligence, and forensic accounting audits. Unauthorized copying, distribution, or external API wrapping is strictly prohibited.