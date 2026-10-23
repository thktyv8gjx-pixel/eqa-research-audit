# EQA 研究档案

**截至 2026-10-23：论文研究准入 NO_GO。** 尚未确认可发表的新机制或方法；没有完整模型复现、训练、具身仿真或视觉证据实验。当前工作已收束为归档，不再继续下载器开发、视频续传或算法研发。

唯一当前决策入口：[EQA_RESEARCH_DECISION.md](EQA_RESEARCH_DECISION.md)。

| 方向 | 保留的历史证据状态 | 当前投入决策 |
| --- | --- | --- |
| D1 缺失证据的行动可恢复性 | HOLD；直接近邻强，缺乏可重置交互与反事实证据 | DROP 当前提案 |
| PTP 单条证据链 | PARTIAL_ONLY；审查已完成 | 关闭重复审查，不进入实验 |
| D2 固定容量跨题记忆 | 尚无独立机制证据 | DROP 宽泛提案；容量限制本身不构成创新 |
| D3 视频前缀证据保留 | HOLD；id4370 没有完整视频、像素/PTS及替代证据核验 | DROP 当前资源路线；停止工程投入 |

DROP 是本项目的投入决定，不是证明整个研究领域没有机会，也不篡改旧报告中的 HOLD / PARTIAL_ONLY。

## 归档导航

- [阶段一报告](reports/phase1.md)、[研究笔记](notes/README.md)、[候选](tables/candidates.csv)与[限制表](tables/limitations.csv)：保留当时记录。
- [阶段二与 D1](EQA_STAGE2_GATE/STAGE2_GATE_REPORT.md)、[查新反证](EQA_STAGE2_GATE/NOVELTY_COUNTEREVIDENCE.md)、[已完成 PTP 审查](EQA_STAGE2_GATE/PTP_SINGLE_TRACE_GATE/GATE_DECISION.md)。
- [Mac 迁移与研究恢复](archive/2026-10-23/local_migration/2026-10-22/RESEARCH_STATE_RECOVERY.md)。
- [D3 文献/协议准入](archive/2026-10-23/D3_ADMISSION_2026-10-23/D3_GATE_REPORT.md)及[最终中止原因](archive/2026-10-23/D3_FINAL_RESUME_PREFLIGHT_2026-10-23_ID4370/D3_SINGLE_CASE_DECISION.md)。中间下载器与离线测试仅作失败过程留档，不作为科学贡献。
- [本次发布清单与转换记录](archive/2026-10-23/PUBLICATION_MANIFEST.json)、[新增受限资产来源索引](archive/2026-10-23/SOURCE_INDEX.json)。

## 完整性与使用边界

本仓库是原创审计成果的发布副本，不是完整 Windows 科研工作区。原始 [RELEASE_MANIFEST.json](RELEASE_MANIFEST.json) 和 [SOURCE_INDEX.json](SOURCE_INDEX.json) 保持不变；来源索引的 192 条记录不等于已恢复 192 份资产。

本次历史发布副本去除了本机路径及完整第三方问题/答案摘录，原始哈希、发布哈希与转换范围逐项登记。历史报告内的哈希对应原件，旧授权或后续建议不继续生效。预算报告 `D3_DOWNLOADER_OFFLINE_2026-10-23/RESUME_BUDGET_AND_VERIFICATION.md` 已发现空文件，未宣称恢复。

第三方论文、原始标注、视频前缀、真实账本、有效配置与私有诊断不上传；仅记录来源、版本、哈希和许可状态。HD-EPIC 项目/存放说明为 CC BY-NC 4.0，而 Bristol 目录字段为 CC BY 4.0，此差异未获权利人澄清。归档不授予这些资产的再发布权。
