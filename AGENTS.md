# Agents Guide - FinAudit AI (v2.0 去伪存真重构)

## 架构一句话
算账归代码（`engine/`，0 LLM，秒级），拍脑袋归 3 个 Agent；命令只留 3 把小刀。v1.x 的 19-Agent 全闭环已归档至 `_legacy/`，备查不执行。

## 三层结构
| 层 | 成员 | 职责 | LLM |
|---|---|---|---|
| Engine（确定性） | `collect/dehydrate/metrics/reconcile/valuation/scenario/render/run_all` | 采集清单、脱水、M-Score/Z-Score/三角探针、对账、Dispatcher定价、情景矩阵、活表 | 0 Token |
| Agent 1 | `forensic-auditor` (subagent) | 脱水问询函+附注交叉+电话会漂移+流水，找矛盾打分 | T2 |
| Agent 2 | `business-strategist` (subagent) | 护城河/增速/指引/Consensus差距，回答 Alpha 在哪 | T2 |
| Agent 3 | `magistrate` (Primary, default) | 综合三路输入，拍板结论/折价率/仓位，唯一签收人 | T2 |

- 技能库（21 skills）保留为方法手册，不裁；Agent 只读方法、不重复造轮子。
- 旧 19 Agent 定义见 `.opencode/agents/_legacy/`（只读归档）；旧 `report/screen/dcf/qa/black-account` 命令见 `.opencode/commands/_legacy/`。

## 三把小刀（均 `.json`+`.md` 双入口）
- `audit --ticker=XXX`：秒级排雷。`run_all.py` 先行（RED/YELLOW/GREEN + 目标价 + 仓位帽），猎手定性复核，裁判一页裁决。只答：能不能碰？
- `reconcile --ticker=XXX`：极速对账。纯 `reconcile.py`，输出 `_contradictions.csv`。FAIL 立案，PASS 回“账平”。
- `delta --ticker=XXX`：预期差雷达。指引 vs Consensus，输出 3 条市场没反应的核心变动 + conviction。

## Engine 脚本契约 (`engine/`)
- 输入：`engine/fixtures/<TICKER_PERIOD>/inputs.json`（三表数 + 指引 + 共识 + 信用 + 执行），文本料（notes/enquiry/transcript.txt）、`flows.csv` 可选。
- 输出：沙盒 `workspace/targets/<TICKER_PERIOD>/`（`_verdict.json`、`_fraud_metrics.json`、`_contradictions.csv`、`_valuation.json`、`_sensitivity.csv`、`Valuation_Model.xlsx`、`tagged_flows.csv`）。
- 依赖：见 `engine/requirements.txt`（numpy/pandas/openpyxl）；无网络、无 LLM Key。
- 法则：数字结论 Python-first；金融/REITs/未盈利禁 FCFF-DCF；困境走兜底；利息按期初债务；T=0 单点折算；借券/CTB 门禁；脱敏不出域。

## Guardrails（v2.0 精简版，沿用 v1.x 硬件）
1. 算术与语言分离：Agent 禁止重算 engine 已算的数，违者打回。
2. 证据制：终稿数字必有 FN/Calc/血统链；无证据指控 magistrate 直接 Dismiss。
3. PII 不出域：未脱敏流水禁入任何 LLM。
4. 执行门：无 ADV/CTB 数据不给仓位；CREDIT_DISTRESS 最高观察仓。

## Infrastructure
- **Config**: `opencode.json` (3 agent，default=magistrate) + `engine/requirements.txt`。
- **Safety**: hook 拦截 rm-rf/dd/fork/curl-wget/curl|sh/python网络/env泄漏/git-force；只读自动放行。
- **Env**: `BLACK_ACCOUNT_AUDIT=1`, `AUDIT_MODE=strict`, `FINANCIAL_AUDIT_MODE=strict`。
- **Legacy**: v1.4–v1.9 的 skills/params/workspace 契约全部保留，engine 实现与之对齐；`eval/` Golden 套件仍指向 v1.x 全闭环口径。
