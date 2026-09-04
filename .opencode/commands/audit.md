---
description: 秒级排雷 — 能不能碰？有无暴雷前兆？(engine + 法证猎手，30秒)
agent: magistrate
---

针对 $ARGUMENTS 执行秒级排雷 (与 audit.json 同义，Markdown 入口)。

1. 先跑 `engine/run_all.py`（0 Token秒级）：`_verdict.json` 给 RED/YELLOW/GREEN + red_flags + 目标价 + 仓位帽。
2. `forensic-auditor` 定性复核（脱水问询函/附注交叉/漂移/流水），输出疑点表。
3. `magistrate` 一页裁决：结论 + 折价率 + 仓位；无证据指控直接 Dismiss。
