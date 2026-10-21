# EQA 研究选题与独立审计

面向具身问答（EQA）论文选题的中文研究记录。核验截止 **2026-10-21**。这些是文献、公开资源与协议审查，**没有训练、模型推理、benchmark或仿真实验结果**。

## 先读最新结论

**D1“缺失证据的可恢复性”仍为HOLD；PTP单条记录准入为PARTIAL_ONLY。** 已取得真实JSON与部分图像引用，但没有完整动作—观察链、同状态替代结果和可核剩余预算，不能进入D1最小实验。图片路径、坏前沿标签和一次失败都不能证明不可恢复。

1. [最新准入结论](EQA_STAGE2_GATE/PTP_SINGLE_TRACE_GATE/GATE_DECISION.md)
2. [单条真实记录与源码核对](EQA_STAGE2_GATE/PTP_SINGLE_TRACE_GATE/TRACE_EVIDENCE.md)
3. [仍缺材料与唯一下一步](EQA_STAGE2_GATE/PTP_SINGLE_TRACE_GATE/MISSING_REQUIREMENTS.md)
4. [阶段二整体审计](EQA_STAGE2_GATE/STAGE2_GATE_REPORT.md)、[新颖性反证](EQA_STAGE2_GATE/NOVELTY_COUNTEREVIDENCE.md)、[条件性最小协议](EQA_STAGE2_GATE/MINIMAL_EXPERIMENT_PLAN.md)

阶段一曾优先讨论D1；后续审计撤销了“已有方法创新依据”的优先推荐。保留历史报告用于追溯，阅读时以后续证据和准入结论为准。HOLD不表示创新已经成立，PARTIAL_ONLY也不自动授权算法开发。

## 既有成果

- [阶段一报告](reports/phase1.md)：三个有条件方向；[候选筛选](reports/screening.md)、[公开评审](reports/public_reviews.md)、[检索边界](reports/search_audit.md)。
- [八篇阅读笔记](notes/README.md)。每篇区分论文原文、作者局限、已报告失败和审计者解释；阅读范围有边界。
- [16项候选](tables/candidates.csv)、[24项局限/协议记录](tables/limitations.csv)、[170行阶段二字段矩阵](EQA_STAGE2_GATE/DATA_FIELD_MATRIX.csv)。不同任务单元和字段计数不构成统一性能排行榜或数据可用率。
- [来源索引](SOURCE_INDEX.json)、[发布转换清单](RELEASE_MANIFEST.json)、各阶段工作日志。论文均保留ID或官方URL；未核实内容仍标为未核实。

## 发布范围

本仓库是26份原创成果的发布副本，并附首页、来源与转换索引。已移除本机绝对路径；未包含老师资料、无关旧项目、论文全文/PDF、第三方源码镜像、原始数据行/图包、模型和本机配置。单条PTP报告的公开副本列schema及结论，完整原始数值摘录留在本地，官方JSON可按固定commit/question/step定位。

未打包的本地证据链接已转为官方来源或来源索引；报告中的215/138份hash检查数描述本地审查范围，不表示这些文件已上传。CSV字段名保持原样，其中`local_evidence_file`的机器路径在发布副本中改为官方来源URL。原始材料未覆盖。

这里只分享审计文字和来源定位；没有为上游论文、软件、HM3D或派生图像授予额外许可，未添加未经授权的LICENSE。

## 下一步

停止依赖PTP公开记录推进D1，向导师申请具备同状态重置、合法动作与预算记账能力的交互仿真资源。在许可、可执行环境和记录契约通过核验之前，不开始D1实验。
