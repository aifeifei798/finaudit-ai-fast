---
description: 极速对账 — 抓出主表与附注自相矛盾的数字 (纯engine，0 LLM)
agent: magistrate
---

针对 $ARGUMENTS 跑极速对账 (与 reconcile.json 同义，Markdown 入口)。

执行 `engine/reconcile.py`，输出 `_contradictions.csv`：合计数✓/WC✓/重述标记/指引偏离/Consensus缺口/交叉悬空。
FAIL 即立案，WARN 进观察；全 PASS 回一句“账平，无矛盾”。
